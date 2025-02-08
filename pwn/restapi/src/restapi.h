void restapi_add_route(char *path, void *func);
void restapi_setup(int port);
void restapi_respond(int statuscode, char *content);
void restapi_run();
