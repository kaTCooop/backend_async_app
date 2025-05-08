import sys
sys.path.append("..")

import core, models

from sqlalchemy.orm import sessionmaker


engine = core.engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = models.Base
meta = core.meta