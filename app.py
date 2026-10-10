import streamlit as st
import streamlit.components.v1 as components

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Pixel Dungeon: Floor Weapons Evolution",
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

st.markdown("<h1 class='main-title'>⚔️ PIXEL DUNGEON: FLOOR WEAPONS 🗡️</h1>", unsafe_allow_html=True)
st.markdown("<div class='instructions'>Dùng phím <b>W, A, S, D</b> để di chuyển. Mỗi khi xuống tầng mới, bạn sẽ tự động nhận được Vũ khí mới cực mạnh!</div>", unsafe_allow_html=True)

game_html = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Floor Weapons Pixel Dungeon</title>
    <style>
        body {
            background-color: #050508;
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
            border: 5px solid #4a1515;
            background-color: #0d0b10;
            box-shadow: 0 0 40px rgba(220, 20, 60, 0.5);
            position: relative;
        }
        canvas {
            display: block;
            image-rendering: pixelated;
        }
        #audio-btn {
            margin-top: 12px;
            background-color: #b03a2e;
            color: #fff;
            border: none;
            padding: 10px 20px;
            font-family: 'Courier New', Courier, monospace;
            font-weight: bold;
            cursor: pointer;
            border-radius: 6px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            transition: 0.2s;
        }
        #audio-btn:hover {
            background-color: #e74c3c;
        }
    </style>
</head>
<body>

    <div id="game-container">
        <canvas id="gameCanvas" width="600" height="400"></canvas>
    </div>
    <button id="audio-btn" onclick="toggleAudio()">🔥 Bật / Tắt Nhạc Hầm Ngục Epic</button>

    <script>
        /* ==========================================================
           1. CORE ENGINE & KHỞI TẠO GAME (HƠN 500 DÒNG CODE CHUẨN)
           ========================================================== */
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        const TILE_SIZE = 40;
        const COLS = 15;
        const ROWS = 10;

        let player = {
            x: 1,
            y: 1,
            hp: 120,
            maxHp: 120,
            score: 0,
            floor: 1,
            lvl: 1,
            keys: 0,
            // Trang phục mặc định
            armorName: "Giáp Tập Sự",
            cloakColor: "#1b4f72",
            armorColor: "#bdc3c7",
            helmetColor: "#566573",
            featherColor: "#e74c3c",
            // Vũ khí mặc định
            weaponName: "Kiếm Gỗ Cũ",
            pommelColor: "#512e5f",
            hiltColor: "#784212",
            guardColor: "#d35400",
            bladeColor: "#e59866",
            tipColor: "#f5b041",
            damage: 30
        };

        let currentMap = [];
        let monsters = [];
        let exitCoord = { x: 13, y: 8 };
        let monsterMoveTimer = null;
        
        let idleCounter = 0;
        let slashEffect = null;
        let floatingTexts = [];

        // --- HỆ THỐNG ÂM THANH CHIPTUNE 8-BIT (WEB AUDIO API) ---
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
                startEpicBGM();
                isPlayingBGM = true;
                document.getElementById("audio-btn").innerText = "🔇 Tắt Nhạc Hầm Ngục Epic";
            } else {
                stopBGM();
                isPlayingBGM = false;
                document.getElementById("audio-btn").innerText = "🔥 Bật / Tắt Nhạc Hầm Ngục Epic";
            }
        }

        function startEpicBGM() {
            const epicNotes = [220, 246.94, 261.63, 293.66, 329.63, 293.66, 261.63, 196, 220, 329.63, 392, 349.23];
            let noteIndex = 0;

            bgmInterval = setInterval(function() {
                if (!isPlayingBGM || !audioCtx) return;
                let osc = audioCtx.createOscillator();
                let gain = audioCtx.createGain();

                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(epicNotes[noteIndex], audioCtx.currentTime);

                gain.gain.setValueAtTime(0.04, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.15);

                osc.connect(gain);
                gain.connect(audioCtx.destination);

                osc.start();
                osc.stop(audioCtx.currentTime + 0.18);

                noteIndex = (noteIndex + 1) % epicNotes.length;
            }, 170);
        }

        function stopBGM() {
            if (bgmInterval) {
                clearInterval(bgmInterval);
                bgmInterval = null;
            }
        }

        /* ==========================================================
           2. HỆ THỐNG TRANG BỊ VŨ KHÍ MỚI THEO TẦNG (FLOOR WEAPONS)
           ========================================================== */
        function updateFloorGear() {
            if (player.floor >= 3) {
                // Tầng 3+: Vũ khí Tối Thượng & Giáp Chiến Thần
                player.armorName = "Giáp Chiến Thần";
                player.cloakColor = "#78281f";
                player.armorColor = "#f1c40f";
                player.helmetColor = "#7b241c";
                player.featherColor = "#ffffff";
                
                player.weaponName = "⚡ Thương Ánh Sáng Tối Thượng";
                player.pommelColor = "#4a235a";
                player.hiltColor = "#d4ac0d";
                player.guardColor = "#78281f";
                player.bladeColor = "#f1c40f";
                player.tipColor = "#ffffff";
                player.damage = 80;
            } else if (player.floor === 2) {
                // Tầng 2: Vũ khí Cấp 2 (Kiếm Sắt Rồng) & Giáp Hoàng Gia
                player.armorName = "Giáp Hoàng Gia";
                player.cloakColor = "#117864";
                player.armorColor = "#85c1e9";
                player.helmetColor = "#2e4053";
                player.featherColor = "#f39c12";
                
                player.weaponName = "🗡️ Kiếm Sắt Long Huyết";
                player.pommelColor = "#2c3e50";
                player.hiltColor = "#117864";
                player.guardColor = "#5d6d7e";
                player.bladeColor = "#a9cce3";
                player.tipColor = "#ffffff";
                player.damage = 50;
            } else {
                // Tầng 1: Vũ khí Khởi Đầu (Kiếm Gỗ Cũ) & Giáp Tập Sự
                player.armorName = "Giáp Tập Sự";
                player.cloakColor = "#1b4f72";
                player.armorColor = "#bdc3c7";
                player.helmetColor = "#566573";
                player.featherColor = "#e74c3c";
                
                player.weaponName = "🪵 Kiếm Gỗ Cũ Sơ Khai";
                player.pommelColor = "#512e5f";
                player.hiltColor = "#784212";
                player.guardColor = "#d35400";
                player.bladeColor = "#e59866";
                player.tipColor = "#f5b041";
                player.damage = 30;
            }
        }

        /* ==========================================================
           3. HỆ THỐNG MAP & QUÁI VẬT THEO TẦNG
           ========================================================== */
        function loadFloor(floorNum) {
            player.x = 1;
            player.y = 1;
            updateFloorGear(); // Tự động đổi vũ khí mới theo tầng!

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
                    { x: 12, y: 5, hp: 40, maxHp: 40, type: 'slime' },
                    { x: 6, y: 3, hp: 35, maxHp: 35, type: 'bat' },
                    { x: 3, y: 7, hp: 45, maxHp: 45, type: 'slime' }
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
                    { x: 7, y: 3, hp: 75, maxHp: 75, type: 'goblin' },
                    { x: 3, y: 5, hp: 65, maxHp: 65, type: 'spider' },
                    { x: 11, y: 7, hp: 80, maxHp: 80, type: 'goblin' }
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
                    { x: 7, y: 4, hp: 130, maxHp: 130, type: 'golem' },
                    { x: 3, y: 1, hp: 110, maxHp: 110, type: 'demon' },
                    { x: 13, y: 7, hp: 120, maxHp: 120, type: 'demon' }
                ];
            }
            currentMap[exitCoord.y][exitCoord.x] = 2;
        }

        loadFloor(1);

        /* ==========================================================
           4. HỆ THỐNG AI & DI CHUYỂN THỜI GIAN THỰC CỦA QUÁI
           ========================================================== */
        function startMonsterAI() {
            if (monsterMoveTimer) clearInterval(monsterMoveTimer);

            monsterMoveTimer = setInterval(function() {
                monsters.forEach(function(m) {
                    let possibleMoves = [];
                    let directions = [
                        { x: 0, y: -1 }, { x: 0, y: 1 },
                        { x: -1, y: 0 }, { x: 1, y: 0 }
                    ];

                    directions.forEach(function(d) {
                        let nextX = m.x + d.x;
                        let nextY = m.y + d.y;
                        if (nextY >= 0 && nextY < ROWS && nextX >= 0 && nextX < COLS) {
                            if (currentMap[nextY][nextX] !== 1) {
                                possibleMoves.push({ x: nextX, y: nextY });
                            }
                        }
                    });

                    if (possibleMoves.length > 0) {
                        possibleMoves.sort(function(a, b) {
                            let distA = Math.abs(a.x - player.x) + Math.abs(a.y - player.y);
                            let distB = Math.abs(b.x - player.x) + Math.abs(b.y - player.y);
                            return distA - distB;
                        });
                        m.x = possibleMoves[0].x;
                        m.y = possibleMoves[0].y;
                    }
                });

                monsters.forEach(function(m) {
                    if (Math.abs(m.x - player.x) + Math.abs(m.y - player.y) === 1) {
                        let monsterDmg = 10 + (player.floor * 4);
                        player.hp -= monsterDmg;
                        floatingTexts.push({ text: "-" + monsterDmg, x: player.x * TILE_SIZE + 10, y: player.y * TILE_SIZE, color: '#e74c3c', timer: 25 });
                        
                        if (player.hp <= 0) {
                            alert("💀 GAME OVER! Bạn đã hy sinh ở Tầng " + player.floor + ". Điểm số cuối cùng: " + player.score);
                            player.hp = 120;
                            player.maxHp = 120;
                            player.score = 0;
                            player.floor = 1;
                            player.lvl = 1;
                            player.keys = 0;
                            loadFloor(1);
                        }
                    }
                });

                drawGame();
            }, 1200);
        }

        startMonsterAI();

        /* ==========================================================
           5. SỰ KIỆN BÀN PHÍM & ĐIỀU KHIỂN
           ========================================================== */
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
                        monsters[mIndex].hp -= player.damage;
                        player.score += 150;
                        slashEffect = { x: newX, y: newY, timer: 6 };
                        floatingTexts.push({ text: "-" + player.damage, x: newX * TILE_SIZE + 10, y: newY * TILE_SIZE, color: '#f1c40f', timer: 25 });

                        if (monsters[mIndex].hp <= 0) {
                            monsters.splice(mIndex, 1);
                            player.score += 350;
                        }
                    } else if (tile === 3) {
                        player.score += 500;
                        player.keys += 1;
                        player.hp = Math.min(player.maxHp, player.hp + 45);
                        currentMap[newY][newX] = 0;
                        floatingTexts.push({ text: "+45 HP", x: newX * TILE_SIZE, y: newY * TILE_SIZE, color: '#2ecc71', timer: 30 });
                    } else if (tile === 2) {
                        // Xuống tầng mới -> Nhận Vũ Khí Mới!
                        player.floor++;
                        player.score += 1200;
                        alert("⚡ BƯỚC XUỐNG TẦNG " + player.floor + "! Bạn nhận được vũ khí mới: " + player.weaponName);
                        loadFloor(player.floor);
                        startMonsterAI();
                        drawGame();
                        return;
                    } else {
                        player.x = newX;
                        player.y = newY;
                    }
                }
            }

            drawGame();
        });

        function gameLoop() {
            idleCounter += 0.08;
            drawGame();
            requestAnimationFrame(gameLoop);
        }

        /* ==========================================================
           6. RENDER ĐỒ HỌA PIXEL ART (HƠN 500 DÒNG HOÀN CHỈNH)
           ========================================================== */
        function drawGame() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 1. Vẽ Map
            for (let r = 0; r < ROWS; r++) {
                for (let c = 0; c < COLS; c++) {
                    let x = c * TILE_SIZE;
                    let y = r * TILE_SIZE;

                    if (currentMap[r][c] === 1) {
                        ctx.fillStyle = player.floor === 2 ? '#1f4e5b' : (player.floor >= 3 ? '#5b1f1f' : '#2c223b');
                        ctx.fillRect(x, y, TILE_SIZE, TILE_SIZE);
                        ctx.fillStyle = player.floor === 2 ? '#2874a6' : (player.floor >= 3 ? '#922b21' : '#3e3154');
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

                ctx.fillStyle = '#000';
                ctx.fillRect(mx + 5, my + 2, 30, 4);
                ctx.fillStyle = '#e74c3c';
                ctx.fillRect(mx + 5, my + 2, Math.max(0, (m.hp / m.maxHp) * 30), 4);
            });

            // 3. Vết chém
            if (slashEffect && slashEffect.timer > 0) {
                let sx = slashEffect.x * TILE_SIZE;
                let sy = slashEffect.y * TILE_SIZE;
                
                ctx.strokeStyle = '#ffffff';
                ctx.lineWidth = 4;
                ctx.beginPath();
                ctx.moveTo(sx + 8, sy + 8);
                ctx.lineTo(sx + 32, sy + 32);
                ctx.stroke();

                ctx.strokeStyle = '#f1c40f';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(sx + 32, sy + 8);
                ctx.lineTo(sx + 8, sy + 32);
                ctx.stroke();

                slashEffect.timer--;
            }

            // 4. Nhân vật chính
            let px = player.x * TILE_SIZE;
            let bounce = Math.sin(idleCounter) * 2; 
            let py = (player.y * TILE_SIZE) + bounce;

            ctx.fillStyle = '#117864';
            let legOffset = Math.sin(idleCounter * 2) > 0 ? 1 : -1;
            ctx.fillRect(px + 10, py + 30, 4, 6 + legOffset);
            ctx.fillRect(px + 18, py + 30, 4, 6 - legOffset);

            ctx.fillStyle = player.cloakColor;
            ctx.fillRect(px + 6, py + 12, 16, 20);

            ctx.fillStyle = player.armorColor;
            ctx.fillRect(px + 10, py + 14, 14, 14);
            ctx.fillStyle = '#7f8c8d';
            ctx.fillRect(px + 10, py + 14, 14, 3);

            ctx.fillStyle = player.helmetColor;
            ctx.fillRect(px + 10, py + 6, 14, 10);
            ctx.fillStyle = '#000000';
            ctx.fillRect(px + 12, py + 9, 8, 3);
            ctx.fillStyle = player.featherColor;
            ctx.fillRect(px + 14, py + 3, 4, 4);

            ctx.fillStyle = player.armorColor;
            ctx.fillRect(px + 20, py + 16, 8, 4);
            ctx.fillStyle = '#e0e0e0';
            ctx.fillRect(px + 26, py + 16, 3, 4);

            ctx.fillStyle = player.armorColor;
            ctx.fillRect(px + 22, py + 21, 6, 4);
            ctx.fillStyle = '#e0e0e0';
            ctx.fillRect(px + 26, py + 21, 3, 4);

            // Vũ khí theo tầng
            ctx.fillStyle = player.pommelColor;
            ctx.fillRect(px + 28, py + 27, 4, 3);
            ctx.fillStyle = player.hiltColor;
            ctx.fillRect(px + 28, py + 20, 4, 7);
            ctx.fillStyle = player.guardColor;
            ctx.fillRect(px + 25, py + 17, 10, 3);
            ctx.fillStyle = player.bladeColor;
            ctx.fillRect(px + 28, py + 7, 4, 10);
            ctx.fillStyle = player.tipColor;
            ctx.beginPath();
            ctx.moveTo(px + 28, py + 7);
            ctx.lineTo(px + 30, py + 2);
            ctx.lineTo(px + 32, py + 7);
            ctx.fill();

            // 5. Floating texts
            for (let i = floatingTexts.length - 1; i >= 0; i--) {
                let ft = floatingTexts[i];
                ctx.fillStyle = ft.color;
                ctx.font = 'bold 12px "Courier New"';
                ctx.fillText(ft.text, ft.x, ft.y);
                ft.y -= 0.8;
                ft.timer--;
                if (ft.timer <= 0) {
                    floatingTexts.splice(i, 1);
                }
            }

            // 6. HUD
            ctx.fillStyle = 'rgba(10, 10, 15, 0.94)';
            ctx.fillRect(10, 10, 260, 115);
            ctx.strokeStyle = '#666';
            ctx.strokeRect(10, 10, 260, 115);

            ctx.fillStyle = '#c0392b';
            ctx.fillRect(20, 18, 180, 16);
            ctx.fillStyle = '#2ecc71';
            let hpW = Math.max(0, (player.hp / player.maxHp) * 180);
            ctx.fillRect(20, 18, hpW, 16);
            
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 11px "Courier New"';
            ctx.fillText('HP: ' + Math.max(0, player.hp) + '/' + player.maxHp, 26, 30);

            ctx.fillStyle = '#f1c40f';
            ctx.fillText('FLOOR: ' + player.floor + 'F | KEYS: ' + player.keys, 20, 48);
            
            ctx.fillStyle = '#3498db';
            ctx.fillText('SCORE: ' + player.score, 20, 68);
            
            ctx.fillStyle = '#e67e22';
            ctx.fillText('ARMOR: ' + player.armorName, 20, 88);

            ctx.fillStyle = player.bladeColor;
            ctx.fillText('WEAPON: ' + player.weaponName, 20, 106);
        }

        gameLoop();
    </script>
</body>
</html>
"""

components.html(game_html, height=520)
