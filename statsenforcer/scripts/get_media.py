import os
import sys
import json
import django

sys.path.append("../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "statsenforcer.settings")
from django.conf import settings
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

django.setup()

import playbyplay.models as pbpmodels
from django.db import transaction
import gzip

from StringIO import StringIO

import api_calls
import sendemail

headers = {
    "User-Agent" : "Mozilla/5.0 (X11; U; Linux i686; " + \
        "en-US; rv:1.9.2.24) Gecko/20111107 " + \
        "Linux Mint/9 (Isadora) Firefox/3.6.24",
}


def game_media(gameid):
    nogame = False
    try:
        content = api_calls.get_game_media(gameid)
    except:
        nogame = True
    if not nogame:
        game = pbpmodels.Game.objects.get(gamePk=gameid)
        content = json.loads(content)
        if "media" not in content:
            #sendemail.send_error_email("Missing media data in game {}".format(gameid))
            return
        elif "epg" not in content["media"]:
            #sendemail.send_error_email("Missing epg from media in game {}".format(gameid))
            return
        for element in content["media"]["epg"]:
            # Save Extended highlights
            if element["title"] in ["Extended Highlights", "Recap", "Power Play"]:
                for jmedia in element["items"]:
                    create_highlight(jmedia, game)
        if "milestones" not in content["media"] or "items" not in content["media"]["milestones"]:
            return
        for milestone in content["media"]["milestones"]["items"]:
            if "highlight" in milestone and milestone["highlight"]:
                try:
                    play = pbpmodels.PlayByPlay.objects.get(gamePk=game, eventId=milestone["statsEventId"])
                    create_highlight(milestone["highlight"], game, play)
                except Exception as e:
                    print milestone["statsEventId"]


def create_highlight(element, game=None, play=None):
    media, created = pbpmodels.PlayMedia.objects.get_or_create(external_id=element["id"],
                                                               game=game)
    if play is not None:
        media.play = play.id
    print element["id"], element["type"], element["title"]
    media.external_id = element["id"]
    media.mediatype = element["type"]
    media.title = element["title"]
    media.blurb = element["blurb"]
    media.description = element["description"]
    media.duration = element["duration"]
    try:
        url = element["image"]["cuts"]["1136x640"]["src"]
    except:
        for cut in element["image"]["cuts"]:
            url = element["image"]["cuts"][cut]["src"]
            break
    if created or media.image is None or media.image == "":
        imgname = "{}.jpeg".format(media.external_id)
        img = api_calls.get_image(url)
        directory = ""
        if game is not None:
            yeardir = str(game.gamePk)[0:4]
            gamedir = str(game.gamePk)[5:]
            directory = "{}/{}/".format(yeardir, gamedir)
        media.image.save("{}{}".format(directory, imgname), img)
    media.save()


if __name__ == "__main__":
    # ignoregameids = set(pbpmodels.PlayMedia.objects.values_list("game_id", flat=True).all())
    # for game in pbpmodels.Game.objects.exclude(gamePk__in=ignoregameids).filter(gamePk__gte=2015020501, gameState__in=["5", "6", "7"]):
    #     print game.gamePk
    #     game_media(game.gamePk)
    #     break
    game_media(2016020362)
