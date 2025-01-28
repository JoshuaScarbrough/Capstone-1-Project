from app import app
from models import db, connect_db, Verse


"""Connects our db to our app.py"""
ctx = app.app_context()
ctx.push()
db.drop_all()
db.create_all()

def seedVerse():
    verses = [
        Verse(mood_code = "UP", verse = "romans15:13?translation=kjv"),
        Verse(mood_code = "UP", verse = "psalm100:2?translation=kjv"),
        Verse(mood_code = "UP", verse = "isaiah61:10?translation=kjv"),
        Verse(mood_code = "UP", verse = "psalm118:24?translation=kjv"),
        Verse(mood_code = "UP", verse = "Ephesians5:19?translation=kjv"),
        Verse(mood_code = "UP", verse = "james1:3?translation=kjv"),
        Verse(mood_code = "MIDDLE", verse = "2corinthians4:8?translation=kjv"),
        Verse(mood_code = "MIDDLE", verse = "hebrews13:8?translation=kjv"),
        Verse(mood_code = "MIDDLE", verse = "psalm34:19?translation=kjv"),
        Verse(mood_code = "DOWN", verse = "psalm34:17?translation=kjv"),
        Verse(mood_code = "DOWN", verse = "1peter5:7?translation=kjv"),
        Verse(mood_code = "DOWN", verse = "1corinthians10:13?translation=kjv"),
        Verse(mood_code = "DOWN", verse = "romans5:13?translation=kjv"),
        Verse(mood_code = "DOWN", verse = "revelation21:4?translation=kjv"),
        Verse(mood_code = "DOWN", verse = "jeremiah29:11?translation=kjv"),
    ]

    for verse in verses:
        db.session.add(verse)
        db.session.commit()

""" This what allows our python app to run"""
if __name__ == '__main__':
    seedVerse()