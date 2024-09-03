
from PyQt5.QtCore import pyqtSignal, QEvent, Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QKeySequenceEdit

from devices import allkeys

class CKeySequenceEdit(QKeySequenceEdit):

    onNewKeySet = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.rawEnabled = False

        self.pressedKeycode: int = 0
        self.tmpKeycodes: list[int] = list()

        self.editingFinished.connect(self.finalize)

    #def getUinputKeycode(self) -> int:
    #    # We need to -8 to convert X keycode -> uinput keycode
    #    return self.pressedKeycode - 8

    #def setKeycode(self, uinputKeycode: int) -> None:
    #    # We need to +8 to convert uinput keycode -> X keycode
    #    self.pressedKeycode = uinputKeycode + 8
    #    self.onNewKeySet.emit(self.pressedKeycode)

    #def setKeySequence(self, keySequence: str):
    #    if keySequence.startswith("0x") and self.rawEnabled:
    #        keySequence = "nullkey"
    #    return super().setKeySequence(keySequence)

    def setKeycode(self, keycode: int):
        self.pressedKeycode = keycode
        self.onNewKeySet.emit(self.pressedKeycode)

    def setKeySequence(self, keySequence: str):
        # TODO FIXME this makes no sense
        if self.rawEnabled and keySequence.startswith("0x"):
            keySequence = "nullkey"
        return super().setKeySequence(keySequence)

    def getKeycode(self) -> int:
        return self.pressedKeycode

    def keyPressEvent(self, a0: QKeyEvent):
        print("keypress:", a0.nativeScanCode(), a0.key())

        # only one single non modifier is allowed
        if len(self.tmpKeycodes) > 0: return

        keycode = a0.nativeScanCode() - 8
        if keycode in allkeys.Modifiers and not self.rawEnabled:
            return

        self.pressedKeycode = keycode
        self.tmpKeycodes.append(a0.key())

        self.onNewKeySet.emit(self.pressedKeycode)

        return super().keyPressEvent(a0)

    def event(self, a0: QEvent) -> bool:
        # we need to filter Tab key press manually and send to
        # keyPressEvent because otherwise tab will unfocus the
        # KeySequenceEdit widget, which is not desired behavior
        if a0.type() == QEvent.Type.KeyPress and a0.key() == Qt.Key.Key_Tab:
            self.keyPressEvent(a0)
            return True

        return super().event(a0)

    def clear(self):
        self.pressedKeycode = 0
        self.tmpKeycodes.clear()
        return super().clear()

    def finalize(self):
        self.tmpKeycodes.clear()

        #print("key:", self.toString())
        #print(self.pressedKeycode)

    def isSet(self):
        #return self.keySequence().count() > 0 and self.pressedKeycode > 0
        print(self.keySequence().toString())
        return self.keySequence().count() > 0

    def setNull(self):
        self.setKeycode(0)
        self.setKeySequence("0x0")

    def toString(self):
        string = self.keySequence().toString()

        if self.rawEnabled and not string:
            return f"0x{self.pressedKeycode}"
        else:
            return string