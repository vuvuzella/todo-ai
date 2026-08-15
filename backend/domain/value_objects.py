from typing import Annotated

from pydantic import AfterValidator, AnyUrl

CleanAnyUrl = Annotated[AnyUrl, AfterValidator(lambda x: str(x).rstrip("/"))]
