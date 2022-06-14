from flask import Flask
from flask_restful import Api, Resource, reqparse, abort
import requests

prispevky = {}
id_counter = 100

pridaj_prispevok_arg = reqparse.RequestParser()
pridaj_prispevok_arg.add_argument("userid", type=int, help="Vyzaduje sa userid", required=True)
pridaj_prispevok_arg.add_argument("title", type=str, help="Vyzaduje sa title prispevku", required=True)
pridaj_prispevok_arg.add_argument("body", type=str, help="Vyzaduje sa body prispevku", required=True)

vypis_prispevok_arg = reqparse.RequestParser()
vypis_prispevok_arg.add_argument("userid", type=int)
vypis_prispevok_arg.add_argument("id", type=int)


zmaz_prispevok_arg = reqparse.RequestParser()
zmaz_prispevok_arg.add_argument("userid", type=int)
zmaz_prispevok_arg.add_argument("id", type=int)


uprav_prispevok_arg = reqparse.RequestParser()
uprav_prispevok_arg.add_argument("id", type=int, help = "Vyzaduje sa id prispevku", required=True)
uprav_prispevok_arg.add_argument("body", type=str, help = "Vyzaduje sa novy obsah prispevku", required=True)




class Prispevky(Resource):

    def post(self):
        arg = pridaj_prispevok_arg.parse_args()
        if self.validacia_userid(arg['userid']):
            global id_counter
            prispevok_id = id_counter + 1
            id_counter += 1
            prispevky[prispevok_id] = arg
        else:
            abort('neplatny pouzivatel')

    def get(self):
        arg = vypis_prispevok_arg.parse_args()
        if arg['userid'] == None and arg['id'] == None:
            abort('Prispevok sa nepodarilo najst')

        elif arg['userid']:
            if self.validacia_userid(arg['userid']):
                prispevky_pouzivatela = {}
                for kluc in self.najdi_kluc(arg['userid']):
                    prispevky_pouzivatela[kluc] = prispevky[kluc]
                return prispevky_pouzivatela

            else:
                abort('uzivatel neexistuje')

        else:
            try:
                return prispevky[arg['id']]
            except KeyError:
                odpoved = requests.get('https://jsonplaceholder.typicode.com/posts')
                for post in odpoved.json():
                    if post['id'] == arg['id']:
                        global id_counter
                        prispevky[id_counter] = post
                        id_counter += 1
                        return post
                abort('prispevok s danym id neexistuje')


    def put(self):
        arg = uprav_prispevok_arg.parse_args()
        try:
            prispevky[arg['id']]['body'] = arg['body']
        except KeyError:
            abort('prispevok s danym id neexistuje')


    def delete(self):
        arg = zmaz_prispevok_arg.parse_args()
        if arg['userid'] == None and arg['id'] == None:
            abort('Prispevok sa nepodarilo najst')
        elif arg['userid']:
            if self.validacia_userid(arg['userid']):
                for id in self.najdi_kluc:
                    prispevky.pop(id)
            else:
                return 'uzivatel neexistuje'
        else:
            try:
                prispevky.pop(arg['id'])
            except KeyError:
                abort('Prispevok s danym id neexistuje')


    def validacia_userid(self, userid):
        odpoved = requests.get('https://jsonplaceholder.typicode.com/users')
        for pouzivatel in odpoved.json():
            if pouzivatel['id'] == userid:
                return True
        return False
    
    def najdi_kluc(self, userid):
        vsetky = []
        for id in prispevky:
            if prispevky[id]['userid'] == userid:
                vsetky.append(id)
        return vsetky


app = Flask(__name__)
api = Api(app)

api.add_resource(Prispevky,"/prispevky")

if __name__ == "__main__":
    app.run(debug=True)