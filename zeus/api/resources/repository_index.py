from flask import request
from sqlalchemy.exc import IntegrityError

from zeus import auth
from zeus.config import db
from zeus.exceptions import IdentityNeedsUpgrade
from zeus.models import (
    Identity, ItemOption, Repository, RepositoryAccess, RepositoryBackend, RepositoryProvider,
    RepositoryStatus
)
from zeus.tasks import import_repo
from zeus.utils import ssh
from zeus.utils.github import GitHubClient

from .base import Resource
from ..schemas import GitHubRepositorySchema, RepositorySchema

repo_schema = RepositorySchema(strict=True)
github_repo_schema = GitHubRepositorySchema(strict=True)
repos_schema = RepositorySchema(many=True, strict=True)


class RepositoryIndexResource(Resource):
    def get_github_client(self, user):
        identity = Identity.query.filter(
            Identity.provider == 'github', Identity.user_id == user.id
        ).first()
        if 'repo' not in identity.config['scopes']:
            raise IdentityNeedsUpgrade(
                scope='repo',
                identity=identity,
            )
        return GitHubClient(token=identity.config['access_token'])

    def get(self):
        """
        Return a list of repositories.
        """
        query = Repository.query.all()
        return self.respond_with_schema(repos_schema, query)

    def post(self):
        """
        Create a new repository.
        """
        provider = (request.get_json() or {}).get('provider', 'native')

        if provider == 'github':
            schema = github_repo_schema
        elif provider == 'native':
            schema = repo_schema
        else:
            raise NotImplementedError

        result = self.schema_from_request(schema, partial=True)
        if result.errors:
            return self.respond(result.errors, 403)
        data = result.data

        user = auth.get_current_user()
        assert user

        if provider == 'github':
            try:
                github = self.get_github_client(user)
            except IdentityNeedsUpgrade as exc:
                return self.respond(
                    {
                        'error': 'identity_needs_upgrade',
                        'url': exc.get_upgrade_url(),
                    }, 401
                )

            # fetch repository details using their credentials
            repo_data = github.get('/repos/{}'.format(data['github_name']))

            repo, created = Repository.query.filter(
                Repository.provider == RepositoryProvider.github,
                Repository.external_id == str(repo_data['id']),
            ).first(), False
            if repo is None:
                # bind various github specific attributes
                repo, created = Repository(
                    backend=RepositoryBackend.git,
                    provider=RepositoryProvider.github,
                    status=RepositoryStatus.active,
                    external_id=str(repo_data['id']),
                    name=repo_data['name'],
                    url=repo_data['clone_url'],
                    data={'github': {
                        'full_name': repo_data['full_name']
                    }},
                ), True
                db.session.add(repo)

                # generate a new private key for use on github
                key = ssh.generate_key()
                db.session.add(
                    ItemOption(
                        item_id=repo.id,
                        name='auth.private-key',
                        value=key.private_key,
                    )
                )

                # register key with github
                github.post(
                    '/repos/{}/keys'.format(repo.data['github']['full_name']),
                    json={
                        'title': 'zeus',
                        'key': key.public_key,
                        'read_only': True,
                    }
                )
        elif provider == 'native':
            raise NotImplementedError

        db.session.flush()

        try:
            with db.session.begin_nested():
                db.session.add(RepositoryAccess(
                    repository=repo,
                    user=auth.get_current_user(),
                ))
                db.session.flush()
        except IntegrityError:
            pass

        db.session.commit()

        if created:
            import_repo.delay(repo_id=repo.id)

        return self.respond_with_schema(repo_schema, repo)
