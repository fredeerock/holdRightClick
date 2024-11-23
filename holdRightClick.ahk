#Requires AutoHotkey v2.0
#SingleInstance Force

clickCount := 0
lastClick := 0
isHolding := false

~LButton:: {
    global clickCount, lastClick, isHolding
    if (isHolding) {
        Send("{RButton Up}")
        isHolding := false
        return
    }
    if (A_TickCount - lastClick < 300) {
        clickCount++
        if (clickCount = 3) {
            clickCount := 0
            Send("{RButton Down}")
            isHolding := true
        }
    } else {
        clickCount := 1
    }
    lastClick := A_TickCount
}

~RButton:: {
    global isHolding
    if (isHolding) {
        Send("{RButton Up}")
        isHolding := false
    }
}

Escape:: {
    global isHolding
    if (isHolding) {
        Send("{RButton Up}")
        isHolding := false
    }
}
