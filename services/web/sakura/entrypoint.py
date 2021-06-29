from werkzeug.security import generate_password_hash
from sqlalchemy.dialects.postgresql import insert as pg_insert

db.session.execute("INSERT INTO calendar(date) SELECT generate_series(to_date('01.01.2021','dd.mm.yyyy'), "
                   "to_date('31.12.2040','dd.mm.yyyy'), '1 day') ON CONFLICT DO NOTHING;")

db.session.execute(pg_insert(User).values(username='admin', password_hash=generate_password_hash('admin')
                                          ).on_conflict_do_nothing())
db.session.commit()
