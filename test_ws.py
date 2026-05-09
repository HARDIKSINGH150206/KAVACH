
from websockets.sync.client import connect


def test():
    try:
        with connect("ws://localhost:8000/ws/threat") as ws:
            print("Connected!")
            msg = ws.recv()
            print("Received:", msg)
    except Exception as e:
        print("Error:", e)


test()
