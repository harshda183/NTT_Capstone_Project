// Harshda Kumari | Roll No. 2501010218 | K = 18
// 48 pixels wide (3 words), 20 rows high, beginning at screen row 18.
// Show while a key is pressed; clear when no key is pressed.
// SCREEN + 32*18 = 16384 + 576 = 16960.

(START)
@KBD
D=M
@DRAW
D;JGT

// Clear 20 rows. PTR advances by 3 written words + 29 words = 32.
@16960
D=A
@PTR
M=D
@20
D=A
@ROWS
M=D
(CLEAR_ROW)
@3
D=A
@WORDS
M=D
(CLEAR_WORD)
@PTR
A=M
M=0
@PTR
M=M+1
@WORDS
MD=M-1
@CLEAR_WORD
D;JGT
@29
D=A
@PTR
M=D+M
@ROWS
MD=M-1
@CLEAR_ROW
D;JGT
@START
0;JMP

// Draw 20 rows using all-one words (black pixels).
(DRAW)
@16960
D=A
@PTR
M=D
@20
D=A
@ROWS
M=D
(DRAW_ROW)
@3
D=A
@WORDS
M=D
(DRAW_WORD)
@PTR
A=M
M=-1
@PTR
M=M+1
@WORDS
MD=M-1
@DRAW_WORD
D;JGT
@29
D=A
@PTR
M=D+M
@ROWS
MD=M-1
@DRAW_ROW
D;JGT
@START
0;JMP
