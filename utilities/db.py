from deta import Deta
import os

deta = Deta(os.getenv("DETA_BASE_KEY"))
users = deta.Base("users")
