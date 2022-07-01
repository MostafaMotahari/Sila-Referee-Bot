from src.sql.session import get_db
from src.sql.models import *

def test():
    db = get_db().__next__()

    user = UserModel(
        username="nmdds",
        first_name="sdfsdfds",
        last_name="sdfsdfds",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    image = MatchImage(
        image_url="sdfsdfdds",
        image_name="sdfsdfds",
        image_type="sdfsdfds",
        match_id=0,
    )

    db.add(image)
    db.commit()
    db.refresh(image)

    match = MatchModel(
        referee=1,
        league=1,
    )

    db.add(match)
    db.commit()
    db.refresh(match)

    match_day = MatchDayModel()


    db.add(match_day)
    db.commit()
    db.refresh(match_day)