// Box.asm  --  K = 71
// Box: starts at row 71, 20 rows tall, 16*((71 mod 4)+1) = 64 pixels wide (4 words)
// While any key is pressed the box is black; when released it is white.

(LOOP)
    // ---- decide colour: color = -1 if key pressed, else 0 ----
    @KBD
    D=M
    @BLACK
    D;JNE
    @color
    M=0
    @START
    0;JMP
(BLACK)
    @color
    M=-1

(START)
    // addr = SCREEN + 32*71 = SCREEN + 2272  (first word of row 71)
    @2272
    D=A
    @SCREEN
    D=D+A
    @addr
    M=D
    // row = 0   (counts 20 rows)
    @row
    M=0

(ROWLOOP)
    // paint the 4 words of this row
    @color
    D=M
    @addr
    A=M
    M=D          // word 0
    A=A+1
    M=D          // word 1
    A=A+1
    M=D          // word 2
    A=A+1
    M=D          // word 3

    // addr = addr + 32  (next row)
    @32
    D=A
    @addr
    M=D+M

    // row = row + 1 ; if row < 20 repeat
    @row
    M=M+1
    D=M
    @20
    D=D-A
    @ROWLOOP
    D;JLT

    @LOOP
    0;JMP
