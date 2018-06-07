import json
import os

import falcon
import psycopg2
import psycopg2.extras


class HealthHandler(object):

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200


class TodosHandler(object):

    def on_get(self, req, resp):
        conn = psycopg2.connect(host=os.environ["DB_HOST"],
                                dbname=os.environ["DB_NAME"],
                                user=os.environ["DB_USER"],
                                password=os.environ["DB_PASSWORD"])
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM public.todo")
        todos = cur.fetchall()
        cur.close()
        conn.close()
        resp.set_header('Content-Type', 'application/json')
        resp.body = json.dumps(todos, sort_keys=False)
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        body = json.loads(req.req_body)
        conn = psycopg2.connect(host=os.environ["DB_HOST"],
                                dbname=os.environ["DB_NAME"],
                                user=os.environ["DB_USER"],
                                password=os.environ["DB_PASSWORD"])
        cur = conn.cursor()
        cur.execute("INSERT INTO public.todo (title, status) VALUES ('{}', '{}')"
            .format(body['title'], body['status']))
        conn.commit()
        cur.close()
        conn.close()
        resp.status = falcon.HTTP_200

    def on_put(self, req, resp, todoID):
        body = json.loads(req.req_body)
        try:
            if not set(['title', 'status']).issubset(body.keys()):
                raise Exception('request does not have a title or status')
            body['id'] = int(todoID)
            conn = psycopg2.connect(host=os.environ["DB_HOST"],
                                    dbname=os.environ["DB_NAME"],
                                    user=os.environ["DB_USER"],
                                    password=os.environ["DB_PASSWORD"])
            cur = conn.cursor()
            cur.execute(
                """Update public.todo set title = '{title}',
                status = '{status}' where id = {id}""".format(**body))
        except Exception as err:
            resp.set_header('Content-Type', 'application/json')
            resp.body = json.dumps({
                u'ERROR': err}, sort_keys=False)
            resp.status = falcon.HTTP_404

        finally:
            if cur.rowcount == 1:
                conn.commit()
                resp.set_header('Content-Type', 'application/json')
                resp.body = json.dumps(body)
                resp.status = falcon.HTTP_200
            else:
                resp.status = falcon.HTTP_404
            cur.close()
            conn.close()
