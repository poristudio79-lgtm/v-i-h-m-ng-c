import streamlit as st
import streamlit.components.v1 as components

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Pixel Dungeon: Moving Monsters & BGM",
    page_icon="⚔️",
    layout="centered"
)

st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #f1c40f;
        font-family: 'Courier New', Courier, monospace;
    }
    .instructions {
        text-align: center;
        color: #ccc;
        font-size: 14px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>⚔️ PIXEL DUNGEON: MOVING MONSTERS & BGM 🗡️</h1>", unsafe_allow_html=True)
st.markdown("<div class='instructions'>Dùng phím <b>W, A, S, D</b> hoặc <b>Phím Mũi Tên</b>. Quái vật sẽ di chuyển theo bạn! Bấm nút bên dưới để bật nhạc nền!</div>", unsafe_allow_html=True)

game_html = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Pixel Dungeon Advanced</title>
    <style>
        body {
            background-color: #0b0b0e;
            color: #ffffff;
            font-family: 'Courier New', Courier, monospace;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin: 0;
            padding: 10px;
            overflow: hidden;
        }
        #game-container {
            border: 4px solid #3d2817;
            background-color: #121016;
            box-shadow: 0 0 30px rgba(0, 0, 0, 0.9);
            position: relative;
        }
        canvas {
            display: block;
            image-rendering: pixelated;
        }
        #audio-btn {
            margin-top: 10px;
            background-color: #f1c40f;
            color: #000;
            border: none;
            padding: 8px 16px;
            font-family: 'Courier New', Courier, monospace;
            font-weight: bold;
            cursor: pointer;
            border-radius: 4px;
        }
        #audio-btn:hover {
            background-color: #d4ac0d;
        }
    </style>
</head>
<body>

    <div id="game-container">
        <canvas id="gameCanvas" width="600" height="400"></canvas>
    </div>
    <button id="audio-btn" onclick="toggleAudio()">🔊 Bật / Tắt Nhạc Nền 8-bit</button>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        const TILE_SIZE = 40;
        const COLS = 15;
        const ROWS = 10;

        let player = {
            x: 1,
            y: 1,
            hp: 100,
            maxHp: 100,
            score: 0,
            floor: 1,
            keys: 0,
            weaponName: "Kiếm Gỗ Cũ",
            weaponColor: "#cd6155",
            damage: 25
        };

        let currentMap = [];
        let monsters = [];
        let exitCoord = { x: 13, y: 8 };

        // --- HỆ THỐNG ÂM THANH NHẠC NỀN 8-BIT (WEB AUDIO API) ---
        let audioCtx = null;
        let isPlayingBGM = false;
        let bgmInterval = null;

        function toggleAudio() {
            if (!isPlayingBGM) {
                if (!audioCtx) {
                    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                }
                if (audioCtx.state === 'suspended') {
                    audioCtx.resume();
                }
                startBGM();
                isPlayingBGM = true;
                document.getElementById("audio-btn").innerText = "🔇 Tắt Nhạc Nền";
            } else {
                stopBGM();
                isPlayingBGM = false;
                document.getElementById("audio-btn").innerText = "🔊 Bật Nhạc Nền 8-bit";
            }
        }

        function startBGM() {
            // Giai điệu nhạc hầm ngục cổ điển (Chiptune arpeggio)
            const notes = [110, 130.81, 146.83, 164.81, 130.81, 98.00, 110, 146.83];
            let noteIndex = 0;

            bgmInterval = setInterval(() => {
                if (!isPlayingBGM || !audioCtx) return;
                let osc = audioCtx.createOscillator();
                let gain = audioCtx.createGain();

                osc.type = 'square'; // Âm thanh kiểu máy game 4 nút cổ điển
                osc.frequency.setValueAtTime(notes[noteIndex], audioCtx.currentTime);

                gain.gain.setValueAtTime(0.05, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.2);

                osc.connect(gain);
                gain.connect(audioCtx.destination);

                osc.start();
                osc.stop(audioCtx.currentTime + 0.25);

                noteIndex = (noteIndex + 1) % notes.length;
            }, 300);
        }

        function stopBGM() {
            if (bgmInterval) {
                clearInterval(bgmInterval);
                bgmInterval = null;
            }
        }
        // --------------------------------------------------------

        function updateWeapon() {
            if (player.keys >= 2) {
                player.weaponName = "Thương Thần Thánh";
                player.weaponColor = "#f1c40f";
                player.damage = 65;
            } else if (player.keys === 1) {
                player.weaponName = "Kiếm Sắt Sắc";
                player.weaponColor = "#3498db";
                player.damage = 40;
            } else {
                player.weaponName = "Kiếm Gỗ Cũ";
                player.weaponColor = "#cd6155";
                player.damage = 25;
            }
        }

        function loadFloor(floorNum) {
            player.x = 1;
            player.y = 1;
            updateWeapon();

            if (floorNum === 1) {
                currentMap = [
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                    [1,0,0,0,1,0,0,0,3,0,1,0,0,2,1],
                    [1,0,1,0,1,0,1,1,0,0,1,0,1,0,1],
                    [1,0,1,0,0,0,0,1,0,0,0,0,1,0,1],
                    [1,0,1,1,1,1,0,1,1,1,0,1,1,0,1],
                    [1,0,0,0,0,1,0,0,0,1,0,0,0,0,1],
                    [1,1,1,0,1,1,1,1,0,1,1,1,1,0,1],
                    [1,3,0,0,0,0,0,1,0,0,0,0,3,0,1],
                    [1,0,1,1,1,1,0,0,0,1,1,1,1,0,1],
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
                ];
                exitCoord = { x: 13, y: 1 };
                monsters = [
                    { x: 12, y: 5, hp: 30, maxHp: 30, type: 'slime' },
                    { x: 6, y: 3, hp: 25, maxHp: 25, type: 'bat' },
                    { x: 3, y: 7, hp: 35, maxHp: 35, type: 'slime' }
                ];
            } else if (floorNum === 2) {
                currentMap = [
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                    [1,0,1,0,0,0,1,0,0,0,3,0,0,0,1],
                    [1,0,1,1,1,0,1,0,1,1,1,1,1,0,1],
                    [1,0,0,0,1,0,0,0,1,0,0,0,1,0,1],
                    [1,1,1,0,1,1,1,0,1,0,1,0,1,0,1],
                    [1,3,0,0,0,0,1,0,0,0,1,0,0,2,1],
                    [1,0,1,1,1,0,1,1,1,1,1,1,1,0,1],
                    [1,0,0,0,1,0,0,0,0,0,0,0,1,0,1],
                    [1,1,1,0,3,1,1,1,1,1,1,0,3,0,1],
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
                ];
                exitCoord = { x: 13, y: 5 };
                monsters = [
                    { x: 7, y: 3, hp: 60, maxHp: 60, type: 'goblin' },
                    { x: 3, y: 5, hp: 50, maxHp: 50, type: 'spider' },
                    { x: 11, y: 7, hp: 70, maxHp: 70, type: 'goblin' }
                ];
            } else {
                currentMap = [
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                    [1,0,0,0,0,0,1,3,0,0,0,0,1,2,1],
                    [1,0,1,1,1,0,1,1,1,0,1,0,1,0,1],
                    [1,0,1,3,1,0,0,0,1,0,1,0,1,0,1],
                    [1,0,1,0,1,1,1,0,1,0,1,1,1,0,1],
                    [1,0,0,0,0,0,1,0,0,0,0,0,0,0,1],
                    [1,1,1,1,1,0,1,1,1,1,1,0,1,1,1],
                    [1,0,0,0,1,0,0,0,3,0,1,0,0,3,1],
                    [1,0,1,0,1,1,1,1,1,0,1,1,1,0,1],
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
                ];
                exitCoord = { x: 13, y: 1 };
                monsters = [
                    { x: 7, y: 4, hp: 110, maxHp: 110, type: 'golem' },
                    { x: 3, y: 1, hp: 90, maxHp: 90, type: 'demon' },
                    { x: 13, y: 7, hp: 100, maxHp: 100, type: 'demon' }
                ];
            }
            currentMap[exitCoord.y][exitCoord.x] = 2;
        }

        loadFloor(1);

        // --- LOGIC DI CHUYỂN CỦA QUÁI VẬT ---
        function moveMonsters() {
            monsters.forEach(m => {
                // Quái di chuyển hướng về phía người chơi (AI đơn giản)
                let possibleMoves = [];
                let directions = [
                    { x: 0, y: -1 }, { x: 0, y: 1 },
                    { x: -1, y: 0 }, { x: 1, y: 0 }
                ];

                directions.forEach(d => {
                    let nextX = m.x + d.x;
                    let nextY = m.y + d.y;
                    if (nextY >= 0 && nextY < ROWS && nextX >= 0 && nextX < COLS) {
                        if (currentMap[nextY][nextX] !== 1) {
                            possibleMoves.push({ x: nextX, y: nextY });
                        }
                    }
                });

                if (possibleMoves.length > 0) {
                    // Ưu tiên chọn ô gần người chơi nhất để đuổi theo
                    possibleMoves.sort((a, b) => {
                        let distA = Math.abs(a.x - player.x) + Math.abs(a.y - player.y);
                        let distB = Math.abs(b.x - player.x) + Math.abs(b.y - player.y);
                        return distA - distB;
                    });
                    // Di chuyển đến ô tối ưu
                    m.x = possibleMoves[0].x;
                    m.y = possibleMoves[0].y;
                }
            });
        }
        // ------------------------------------

        // Xử lý sự kiện bàn phím
        window.addEventListener('keydown', function(e) {
            if(["Space","ArrowUp","ArrowDown","ArrowLeft","ArrowRight","w","a","s","d"].indexOf(e.key) > -1) {
                e.preventDefault();
            }

            let newX = player.x;
            let newY = player.y;

            if (e.key === 'ArrowUp' || e.key === 'w' || e.key === 'W') newY--;
            if (e.key === 'ArrowDown' || e.key === 's' || e.key === 'S') newY++;
            if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') newX--;
            if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') newX++;

            if (newY >= 0 && newY < ROWS && newX >= 0 && newX < COLS) {
                let tile = currentMap[newY][newX];

                if (tile !== 1) {
                    let mIndex = monsters.findIndex(m => m.x === newX && m.y === newY);
                    if (mIndex !== -1) {
                        // Tấn công quái
                        monsters[mIndex].hp -= player.damage;
                        player.score += 100;
                        if (monsters[mIndex].hp <= 0) {
                            monsters.splice(mIndex, 1);
                            player.score += 250;
                        }
                    } else if (tile === 3) {
                        // Nhặt rương
                        player.score += 400;
                        player.keys += 1;
                        player.hp = Math.min(player.maxHp, player.hp + 35);
                        currentMap[newY][newX] = 0;
                        updateWeapon();
                    } else if (tile === 2) {
                        // Xuống tầng mới
                        player.floor++;
                        player.score += 1000;
                        alert("⚡ Sang Tầng " + player.floor + "! Vũ khí hiện tại: " + player.weaponName);
                        loadFloor(player.floor);
                        drawGame();
                        return;
                    } else {
                        player.x = newX;
                        player.y = newY;
                    }

                    // Sau khi người chơi di chuyển xong, quái tiến hành di chuyển đuổi theo
                    moveMonsters();
                }
            }

            // Kiểm tra quái tấn công người chơi
            monsters.forEach(function(m) {
                if (Math.abs(m.x - player.x) + Math.abs(m.y - player.y) === 1) {
                    let monsterDmg = 12 + (player.floor * 4);
                    player.hp -= monsterDmg;
                    if (player.hp <= 0) {
                        alert("💀 Game Over! Bạn đã hy sinh ở Tầng " + player.floor + ". Điểm: " + player.score);
                        player.hp = 100;
                        player.score = 0;
                        player.floor = 1;
                        player.keys = 0;
                        loadFloor(1);
                    }
                }
            });

            drawGame();
        });

        // Vẽ giao diện game
        function drawGame() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 1. Vẽ bản đồ hầm ngục
            for (let r = 0; r < ROWS; r++) {
                for (let c = 0; c < COLS; c++) {
                    let x = c * TILE_SIZE;
                    let y = r * TILE_SIZE;

                    if (currentMap[r][c] === 1) {
                        ctx.fillStyle = player.floor === 2 ? '#22313f' : (player.floor >= 3 ? '#4a1515' : '#2c223b');
                        ctx.fillRect(x, y, TILE_SIZE, TILE_SIZE);
                        ctx.fillStyle = '#3e3154';
                        ctx.fillRect(x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4);
                    } else {
                        ctx.fillStyle = '#1b1726';
                        ctx.fillRect(x, y, TILE_SIZE, TILE_SIZE);
                        ctx.strokeStyle = '#252033';
                        ctx.strokeRect(x, y, TILE_SIZE, TILE_SIZE);
                    }

                    if (currentMap[r][c] === 2) {
                        ctx.fillStyle = '#f1c40f';
                        ctx.fillRect(x + 4, y + 4, TILE_SIZE - 8, TILE_SIZE - 8);
                    }

                    if (currentMap[r][c] === 3) {
                        ctx.fillStyle = '#d35400';
                        ctx.fillRect(x + 8, y + 12, 24, 18);
                        ctx.fillStyle = '#f39c12';
                        ctx.fillRect(x + 16, y + 18, 8, 6);
                    }
                }
            }

            // 2. Vẽ quái vật
            monsters.forEach(function(m) {
                let mx = m.x * TILE_SIZE;
                let my = m.y * TILE_SIZE;

                if (m.type === 'slime') {
                    ctx.fillStyle = '#e74c3c';
                    ctx.beginPath();
                    ctx.arc(mx + 20, my + 25, 12, Math.PI, 0, false);
                    ctx.fill();
                } else if (m.type === 'bat') {
                    ctx.fillStyle = '#9b59b6';
                    ctx.fillRect(mx + 10, my + 15, 20, 10);
                } else if (m.type === 'goblin') {
                    ctx.fillStyle = '#27ae60';
                    ctx.fillRect(mx + 12, my + 10, 16, 20);
                } else if (m.type === 'spider') {
                    ctx.fillStyle = '#34495e';
                    ctx.fillRect(mx + 10, my + 12, 20, 14);
                } else {
                    ctx.fillStyle = '#e67e22';
                    ctx.fillRect(mx + 8, my + 6, 24, 28);
                }

                // Thanh máu nhỏ của quái
                ctx.fillStyle = '#000';
                ctx.fillRect(mx + 5, my + 2, 30, 4);
                ctx.fillStyle = '#e74c3c';
                ctx.fillRect(mx + 5, my + 2, Math.max(0, (m.hp / m.maxHp) * 30), 4);
            });

            // 3. Vẽ nhân vật hiệp sĩ và vũ khí
            let px = player.x * TILE_SIZE;
            let py = player.y * TILE_SIZE;
            
            ctx.fillStyle = '#2980b9';
            ctx.fillRect(px + 8, py + 12, 24, 20);
            ctx.fillStyle = '#bdc3c7';
            ctx.fillRect(px + 12, py + 8, 16, 16);
            ctx.fillStyle = '#8e44ad';
            ctx.fillRect(px + 12, py + 4, 16, 8);
            
            ctx.fillStyle = player.weaponColor;
            ctx.fillRect(px + 28, py + 12, 10, 6);

            // 4. Vẽ khung giao diện HUD
            ctx.fillStyle = 'rgba(15, 15, 20, 0.92)';
            ctx.fillRect(10, 10, 240, 100);
            ctx.strokeStyle = '#555';
            ctx.strokeRect(10, 10, 240, 100);

            ctx.fillStyle = '#c0392b';
            ctx.fillRect(20, 18, 160, 16);
            ctx.fillStyle = '#2ecc71';
            let hpW = Math.max(0, (player.hp / player.maxHp) * 160);
            ctx.fillRect(20, 18, hpW, 16);
            
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 11px "Courier New"';
            ctx.fillText('HP: ' + Math.max(0, player.hp) + '/' + player.maxHp, 26, 30);

            ctx.fillStyle = '#f1c40f';
            ctx.fillText('SCORE: ' + player.score, 20, 48);
            
            ctx.fillStyle = '#3498db';
            ctx.fillText('FLOOR: ' + player.floor + 'F', 140, 48);
            
            ctx.fillStyle = '#e67e22';
            ctx.fillText('KEYS: ' + player.keys, 20, 68);

            ctx.fillStyle = player.weaponColor;
            ctx.fillText('WEAPON: ' + player.weaponName, 20, 90);
        }

        drawGame();
    </script>
</body>
</html>
"""

components.html(game_html, height=490)
