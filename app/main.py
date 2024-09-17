import config
from api import router
from api.graphql.resolvers import resolvers
from db.base import get_session
from fastapi import FastAPI
from patisson_appLauncher.fastapi_app_launcher import UvicornFastapiAppLauncher


app = FastAPI(title=config.SERVICE_NAME)


if __name__ == "__main__":
    app_launcher = UvicornFastapiAppLauncher(app, router,
                        service_name=config.SERVICE_NAME,
                        host=config.SERVICE_HOST)
    app_launcher.add_sync_consul_health_path()
    app_launcher.consul_register()
    app_launcher.add_jaeger()
    app_launcher.add_async_ariadne_graphql_route(
        resolvers=resolvers, 
        session_gen=get_session,
        debug=True
    )
    app_launcher.include_router()
    app_launcher.app_run()