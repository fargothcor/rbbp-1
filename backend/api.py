import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpserver
import db

class WebSocket(tornado.websocket.WebSocketHandler):
    def game_info(self):
        game = db.models.Game.select().first()
        team_attacker = db.models.Team.select().where(db.models.Team.type == 'red').first().name
        team_defencer = db.models.Team.select().where(db.models.Team.type == 'blue').first().name
        score = game.score
        rounds = game.round or 1
        tasks_data = []
        tasks = db.models.Task.select()
        for task in tasks:
            task_name = task.name
            task_status = task.status
            count_of_flags = db.models.Submit.select().where(db.models.Submit.flag in db.models.Flag.select().where(db.models.Flag.task == task)).count()
            task_sla = round((db.models.Check.select().where(db.models.Check.command == 'get' and db.models.Check.status == 100).count()/rounds)*100, 2)
            tasks_data.append({'task_name': task_name, 'count_of_flags': count_of_flags, 'status': task_status, 'sla': task_sla})
        return self.write_message(str({'team_attacker': team_attacker, 'team_defencer':team_defencer, 'score': score, 'round': rounds, 'tasks': tasks_data}))

    def open(self):
        self.game_info()

if __name__ == "__main__":
    app = tornado.web.Application([
        (r"/", WebSocket),
    ])

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()