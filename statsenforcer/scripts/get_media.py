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
    #content = api_calls.get_game_media(gameid)
    game = pbpmodels.Game.objects.get(gamePk=gameid)
    fp = open("/vagrant/content.html")
    content = fp.read()
    fp.close()
    content = json.loads(content)
    if "media" not in content:
        #sendemail.send_error_email("Missing media data in game {}".format(gameid))
        raise Exception("Missing media!")
    elif "epg" not in content["media"]:
        #sendemail.send_error_email("Missing epg from media in game {}".format(gameid))
        raise Exception("Missing epg!")
    for element in content["media"]["epg"]:
        # Save Extended highlights
        if element["title"] in ["Extended Highlights", "Recap", "Power Play"]:
            for jmedia in element["items"]:
                create_highlight(jmedia, game)
    for milestone in content["media"]["milestones"]["items"]:
        if milestone["highlight"]:
            play = pbpmodels.PlayByPlay.objects.get(gamePk=game, eventIdx=milestone["statsEventId"])
            create_highlight(element, game, play)


def create_highlight(element, game=None, play=None):
    media, created = pbpmodels.PlayMedia.objects.get_or_create(external_id=element["id"],
                                                               game=game)
    if play is not None:
        media.play = play
    media.external_id = element["id"]
    media.media_type = element["type"]
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
    imgname = "{}.jpeg".format(media.external_id)
    img_temp = NamedTemporaryFile(delete=True)
    img_temp.write(api_calls.get_image(url, imgname))
    img_temp.flush()
    media.image.save(imgname, File(img_temp))
    media.save()


if __name__ == "__main__":
    game_media(2016020220)
