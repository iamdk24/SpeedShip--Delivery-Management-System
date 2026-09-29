from fastapi import FastAPI, HTTPException, Request, Response,status


class SpeedShipError(Exception):
    """Base Exception/Error for the SpeesShip Api"""

    status= status.HTTP_400_BAD_REQUEST

class EntityNotFound(SpeedShipError):
    """Entity not found in database"""
    status=status.HTTP_404_NOT_FOUND

class ClientNotAuthorized(SpeedShipError):
    """Client is not authorized to perform the action"""
    status=status.HTTP_401_UNAUTHORIZED

class BadCredentials(SpeedShipError):
    """User email or password is incorrect"""
    status=status.HTTP_401_UNAUTHORIZED

class InvalidToken(SpeedShipError):
    """Access token is invalid or expired"""
    status=status.HTTP_401_UNAUTHORIZED

class DeliveryPartnerNotAvailable(SpeedShipError):
    """Delivery partner/s do not service the destination"""
    status=status.HTTP_406_NOT_ACCEPTABLE

class DeliveryPartnerCapacityExceeded(SpeedShipError):
    """Delivery partner has reached their max handling capacity"""
    status=status.HTTP_406_NOT_ACCEPTABLE

def _get_handler(status: int, detail:str) -> Response:
    def handler(request: Request, exception: Exception)->Response:
        #Debug Print Statement
        from rich import print,panel
        print(
            panel.Panel(exception.__class__.__name__,
                        title="Handled Exception",
                        border_style="red"),
        )


        raise HTTPException(status_code=status,
                            detail=detail)

    return handler

def add_exception_handlers(app: FastAPI):
    exception_classes=SpeedShipError.__subclasses__()

    for exception_class in exception_classes:

        app.add_exception_handler(
            exception_class,
            _get_handler(status=exception_class.status,
                         detail=exception_class.__doc__)
        )

