import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Pixel Dungeon: Cerberus Boss Edition",
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

st.markdown("<h1 class='main-title'>⚔️ PIXEL DUNGEON: CERBERUS BOSS EDITION 🗡️</h1>", unsafe_allow_html=True)
st.markdown("<div class='instructions'>Dùng phím <b>W, A, S, D</b> di chuyển. Tầng 10: Sống sót và chiến đấu với <b>Chó 3 Đầu (Cerberus)</b> trong 1 phút để phá đảo!</div>", unsafe_allow_html=True)

game_html = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Pixel Dungeon Cerberus Boss</title>
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
            cursor: pointer;
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
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        const TILE_SIZE = 40;
        const COLS = 15;
        const ROWS = 10;

        let player = {
            x: 1,
            y: 1,
            hp: 200,
            maxHp: 200,
            score: 0,
            floor: 1,
            keys: 0,
            armorName: "",
            cloakColor: "",
            armorColor: "",
            helmetColor: "",
            featherColor: "",
            weaponName: "",
            weaponType: "sword",
            pommelColor: "",
            hiltColor: "",
            guardColor: "",
            bladeColor: "",
            tipColor: "",
            damage: 35
        };

        let currentMap = [];
        let monsters = [];
        let exitCoord = { x: 13, y: 8 };
        let monsterMoveTimer = null;
        let gameWon = false;
        let inTransitionMenu = false;
        
        // Trạng thái Boss Tầng 10 (Chó 3 đầu Cerberus)
        let isBossFloor = false;
        let bossFightStarted = false;
        let bossTimer = 60; // 60 giây sinh tử
        let bossTimerInterval = null;
        let bossHp = 3000;
        let bossMaxHp = 3000;
        let bossDefeatedAnimation = false;

        let idleCounter = 0;
        let slashEffect = null;
        let floatingTexts = [];

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

        const floorGearDatabase = {
            1: {
                armorName: "Giáp Tập Sự", cloak: "#1b4f72", armor: "#bdc3c7", helmet: "#566573", feather: "#e74c3c",
                weaponName: "🪵 Kiếm Gỗ Sơ Khai", weaponType: "sword", damage: 35, pommel: "#512e5f", hilt: "#784212", guard: "#d35400", blade: "#e59866", tip: "#f5b041"
            },
            2: {
                armorName: "Giáp Da Rừng Sâu", cloak: "#145a32", armor: "#7d6608", helmet: "#4d5656", feather: "#2ecc71",
                weaponName: "🗡️ Dao Găm Thợ Săn", weaponType: "dagger", damage: 50, pommel: "#1b4f72", hilt: "#7d6608", guard: "#b7950b", blade: "#a6acaf", tip: "#ffffff"
            },
            3: {
                armorName: "Giáp Đồng Cổ Kính", cloak: "#78281f", armor: "#d35400", helmet: "#641e16", feather: "#f1c40f",
                weaponName: "⚔️ Kiếm Đồng Cổ", weaponType: "sword", damage: 70, pommel: "#641e16", hilt: "#b9770e", guard: "#d35400", blade: "#f39c12", tip: "#fcf3cf"
            },
            4: {
                armorName: "Giáp Sắt Kiên Cố", cloak: "#2e4053", armor: "#85c1e9", helmet: "#1b4f72", feather: "#3498db",
                weaponName: "🗡️ Kiếm Sắt Sắc Bén", weaponType: "sword", damage: 90, pommel: "#2c3e50", hilt: "#5d6d7e", guard: "#85c1e9", blade: "#ecf0f1", tip: "#ffffff"
            },
            5: {
                armorName: "Giáp Bạc Ánh Trăng", cloak: "#512e5f", armor: "#d7bde2", helmet: "#4a235a", feather: "#bb8fce",
                weaponName: "🌙 Ngân Kiếm Ánh Trăng", weaponType: "sword", damage: 115, pommel: "#4a235a", hilt: "#8e44ad", guard: "#d7bde2", blade: "#f4ecf7", tip: "#ffffff"
            },
            6: {
                armorName: "Giáp Vàng Hoàng Gia", cloak: "#7d3c98", armor: "#f1c40f", helmet: "#7e5109", feather: "#e74c3c",
                weaponName: "⚡ Kiếm Vàng Hoàng Gia", weaponType: "sword", damage: 140, pommel: "#512e5f", hilt: "#d4ac0d", guard: "#f1c40f", blade: "#fcf3cf", tip: "#ffffff"
            },
            7: {
                armorName: "Giáp Huyết Long", cloak: "#641e16", armor: "#c0392b", helmet: "#512e5f", feather: "#f39c12",
                weaponName: "🔥 Thương Huyết Long", weaponType: "spear", damage: 170, pommel: "#512e5f", hilt: "#922b21", guard: "#c0392b", blade: "#e74c3c", tip: "#f1c40f"
            },
            8: {
                armorName: "Giáp Băng Giá Tận Thế", cloak: "#1b4f72", armor: "#a9cce3", helmet: "#154360", feather: "#ffffff",
                weaponName: "❄️ Băng Kiếm Vĩnh Cửu", weaponType: "sword", damage: 200, pommel: "#154360", hilt: "#2980b9", guard: "#a9cce3", blade: "#ebf5fb", tip: "#ffffff"
            },
            9: {
                armorName: "Giáp Bóng Đêm Tối Thượng", cloak: "#111111", armor: "#34495e", helmet: "#000000", feather: "#9b59b6",
                weaponName: "💀 Hắc Kiếm Vô Thường", weaponType: "sword", damage: 240, pommel: "#000000", hilt: "#2c3e50", guard: "#8e44ad", blade: "#5d6d7e", tip: "#bb8fce"
            },
            10: {
                armorName: "Giáp Thần Thánh Tối Thượng", cloak: "#7d3c98", armor: "#ffffff", helmet: "#d4ac0d", feather: "#e74c3c",
                weaponName: "👑 Kiếm Thần Excalibur", weaponType: "excalibur", damage: 300, pommel: "#512e5f", hilt: "#f1c40f", guard: "#c0392b", blade: "#ffffff", tip: "#f39c12"
            }
        };

        function updatePlayerGear(floorNum) {
            let gear = floorGearDatabase[floorNum] || floorGearDatabase[1];
            player.armorName = gear.armorName;
            player.cloakColor = gear.cloak;
            player.armorColor = gear.armor;
            player.helmetColor = gear.helmet;
            player.featherColor = gear.feather;
            player.weaponName = gear.weaponName;
            player.weaponType = gear.weaponType;
            player.damage = gear.damage;
            player.pommelColor = gear.pommel;
            player.hiltColor = gear.hilt;
            player.guardColor = gear.guard;
            player.bladeColor = gear.blade;
            player.tipColor = gear.tip;
        }

        const extraWeapons = [
            { name: "🪓 Rìu Chiến Thổ Dân", type: "axe", damage: 60, pommel: "#4d5656", hilt: "#784212", guard: "#5d6d7e", blade: "#bdc3c7", tip: "#ffffff" },
            { name: "🏹 Cung Tên Săn Mồi", type: "bow", damage: 85, pommel: "#78281f", hilt: "#b9770e", guard: "#d35400", blade: "#f39c12", tip: "#fcf3cf" },
            { name: "⚡ Giáo Sét Cổ Đại", type: "spear", damage: 120, pommel: "#1b4f72", hilt: "#2874a6", guard: "#5499c7", blade: "#85c1e9", tip: "#ffffff" },
            { name: "🔥 Thương Lửa Địa Ngục", type: "spear", damage: 180, pommel: "#78281f", hilt: "#d35400", guard: "#922b21", blade: "#e67e22", tip: "#f1c40f" },
            { name: "👑 Kiếm Thần Excalibur", type: "excalibur", damage: 280, pommel: "#7d3c98", hilt: "#f1c40f", guard: "#c0392b", blade: "#ffffff", tip: "#f39c12" }
        ];

        function changeWeaponRandomly() {
            let randW = extraWeapons[Math.floor(Math.random() * extraWeapons.length)];
            player.weaponName = randW.name;
            player.weaponType = randW.type;
            player.damage = randW.damage;
            player.pommelColor = randW.pommel;
            player.hiltColor = randW.hilt;
            player.guardColor = randW.guard;
            player.bladeColor = randW.blade;
            player.tipColor = randW.tip;
            alert("✨ Đã đổi vũ khí thành công: " + player.weaponName + " (Sát thương: " + player.damage + ")");
        }

        function drawWeapon(px, py) {
            let type = player.weaponType;

            if (type === "dagger") {
                ctx.fillStyle = player.pommelColor; ctx.fillRect(px + 28, py + 25, 3, 2);
                ctx.fillStyle = player.hiltColor; ctx.fillRect(px + 28, py + 21, 3, 4);
                ctx.fillStyle = player.guardColor; ctx.fillRect(px + 26, py + 19, 7, 2);
                ctx.fillStyle = player.bladeColor; ctx.fillRect(px + 28, py + 13, 3, 6);
                ctx.fillStyle = player.tipColor; ctx.beginPath(); ctx.moveTo(px + 28, py + 13); ctx.lineTo(px + 29.5, py + 9); ctx.lineTo(px + 31, py + 13); ctx.fill();
            } else if (type === "spear") {
                ctx.fillStyle = player.pommelColor; ctx.fillRect(px + 28, py + 30, 4, 3);
                ctx.fillStyle = player.hiltColor; ctx.fillRect(px + 28, py + 12, 4, 18);
                ctx.fillStyle = player.guardColor; ctx.fillRect(px + 26, py + 10, 8, 2);
                ctx.fillStyle = player.bladeColor; ctx.beginPath(); ctx.moveTo(px + 25, py + 10); ctx.lineTo(px + 30, py - 6); ctx.lineTo(px + 35, py + 10); ctx.fill();
                ctx.fillStyle = player.tipColor; ctx.beginPath(); ctx.moveTo(px + 28, py + 4); ctx.lineTo(px + 30, py - 6); ctx.lineTo(px + 32, py + 4); ctx.fill();
            } else if (type === "axe") {
                ctx.fillStyle = player.hiltColor; ctx.fillRect(px + 28, py + 10, 4, 18);
                ctx.fillStyle = player.pommelColor; ctx.fillRect(px + 28, py + 27, 4, 3);
                ctx.fillStyle = player.bladeColor; ctx.beginPath(); ctx.moveTo(px + 30, py + 10); ctx.lineTo(px + 40, py + 4); ctx.lineTo(px + 40, py + 20); ctx.lineTo(px + 30, py + 16); ctx.fill();
                ctx.fillStyle = player.tipColor; ctx.fillRect(px + 39, py + 5, 2, 14);
            } else if (type === "bow") {
                ctx.strokeStyle = player.hiltColor; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(px + 26, py + 16, 12, -Math.PI / 2, Math.PI / 2, false); ctx.stroke();
                ctx.strokeStyle = "#ffffff"; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(px + 26, py + 4); ctx.lineTo(px + 26, py + 28); ctx.stroke();
                ctx.fillStyle = player.tipColor; ctx.fillRect(px + 22, py + 15, 12, 2);
            } else if (type === "excalibur") {
                ctx.fillStyle = "#f1c40f"; ctx.fillRect(px + 27, py + 28, 6, 4);
                ctx.fillStyle = player.hiltColor; ctx.fillRect(px + 28, py + 20, 4, 8);
                ctx.fillStyle = player.guardColor; ctx.fillRect(px + 22, py + 17, 16, 4);
                ctx.fillStyle = "#f39c12"; ctx.fillRect(px + 24, py + 15, 12, 2);
                ctx.fillStyle = player.bladeColor; ctx.fillRect(px + 27, py - 2, 6, 19);
                ctx.fillStyle = player.tipColor; ctx.beginPath(); ctx.moveTo(px + 27, py - 2); ctx.lineTo(px + 30, py - 10); ctx.lineTo(px + 33, py - 2); ctx.fill();
            } else {
                ctx.fillStyle = player.pommelColor; ctx.fillRect(px + 28, py + 27, 4, 3);
                ctx.fillStyle = player.hiltColor; ctx.fillRect(px + 28, py + 20, 4, 7);
                ctx.fillStyle = player.guardColor; ctx.fillRect(px + 25, py + 17, 10, 3);
                ctx.fillStyle = player.bladeColor; ctx.fillRect(px + 28, py + 7, 4, 10);
                ctx.fillStyle = player.tipColor; ctx.beginPath(); ctx.moveTo(px + 28, py + 7); ctx.lineTo(px + 30, py + 2); ctx.lineTo(px + 32, py + 7); ctx.fill();
            }
        }

        function loadFloor(floorNum) {
            player.x = 1;
            player.y = 1;
            updatePlayerGear(floorNum);
            isBossFloor = (floorNum === 10);
            bossFightStarted = false;
            bossDefeatedAnimation = false;
            bossTimer = 60;
            if (bossTimerInterval) clearInterval(bossTimerInterval);

            if (floorNum === 10) {
                currentMap = [
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                    [1,0,1,1,1,0,1,1,1,0,1,1,1,0,1],
                    [1,0,1,0,0,0,0,0,0,0,0,0,1,0,1],
                    [1,0,1,0,1,1,1,1,1,1,1,0,1,0,1],
                    [1,0,1,0,1,0,0,0,0,0,1,0,1,0,1],
                    [1,0,1,0,1,0,3,0,3,0,1,0,1,0,1],
                    [1,0,1,0,1,1,1,1,1,1,1,0,1,0,1],
                    [1,0,0,0,0,0,0,0,0,0,0,0,0,2,1],
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
                ];
                exitCoord = { x: 13, y: 8 };
                monsters = [];
            } else {
                // Map thông thường các tầng 1-9
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
                monsters = [{ x: 12, y: 5, hp: 50, maxHp: 50, type: 'slime' }];
            }
            currentMap[exitCoord.y][exitCoord.x] = 2;
        }

        loadFloor(1);

        canvas.addEventListener('click', function(e) {
            let rect = canvas.getBoundingClientRect();
            let mouseX = e.clientX - rect.left;
            let mouseY = e.clientY - rect.top;

            if (inTransitionMenu) {
                if (mouseX >= 100 && mouseX <= 280 && mouseY >= 220 && mouseY <= 270) {
                    changeWeaponRandomly();
                    drawGame();
                }
                else if (mouseX >= 320 && mouseX <= 500 && mouseY >= 220 && mouseY <= 270) {
                    inTransitionMenu = false;
                    loadFloor(player.floor);
                    startMonsterAI();
                    drawGame();
                }
            }
        });

        function startMonsterAI() {
            if (monsterMoveTimer) clearInterval(monsterMoveTimer);

            monsterMoveTimer = setInterval(function() {
                if (gameWon || inTransitionMenu || isBossFloor) return;

                monsters.forEach(function(m) {
                    let possibleMoves = [];
                    let directions = [{ x: 0, y: -1 }, { x: 0, y: 1 }, { x: -1, y: 0 }, { x: 1, y: 0 }];

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
                        let monsterDmg = 12 + (player.floor * 4);
                        player.hp -= monsterDmg;
                        floatingTexts.push({ text: "-" + monsterDmg, x: player.x * TILE_SIZE + 10, y: player.y * TILE_SIZE, color: '#e74c3c', timer: 25 });
                        
                        if (player.hp <= 0) {
                            alert("💀 GAME OVER! Bạn đã ngã xuống ở Tầng " + player.floor + ". Điểm: " + player.score);
                            player.hp = 150;
                            player.score = 0;
                            player.floor = 1;
                            player.keys = 0;
                            inTransitionMenu = false;
                            loadFloor(1);
                        }
                    }
                });

                drawGame();
            }, 1200);
        }

        startMonsterAI();

        // --- BẮT ĐẦU ĐẤU BOSS TRÙM CUỐI (CHÓ 3 ĐẦU) Ở TẦNG 10 ---
        function startCerberusBossFight() {
            if (bossFightStarted) return;
            bossFightStarted = true;
            bossHp = 3000;
            bossTimer = 60;

            bossTimerInterval = setInterval(function() {
                if (gameWon) return;
                bossTimer--;
                
                // Boss gây sát thương định kỳ mỗi giây lên người chơi
                let bossDmg = 15;
                player.hp -= bossDmg;
                floatingTexts.push({ text: "-" + bossDmg, x: player.x * TILE_SIZE + 10, y: player.y * TILE_SIZE, color: '#e74c3c', timer: 20 });

                if (player.hp <= 0) {
                    clearInterval(bossTimerInterval);
                    alert("💀 Chó 3 Đầu Cerberus đã đánh bại bạn ở Tầng 10!");
                    player.hp = 200;
                    player.floor = 1;
                    loadFloor(1);
                    return;
                }

                if (bossTimer <= 0) {
                    clearInterval(bossTimerInterval);
                    bossDefeatedAnimation = true;
                    // Nhân vật tung đòn kết liễu đâm chết Chó 3 Đầu sau 1 phút
                    setTimeout(function() {
                        gameWon = true;
                        stopBGM();
                        drawGame();
                    }, 2000);
                }
            }, 1000);
        }

        window.addEventListener('keydown', function(e) {
            if (gameWon || inTransitionMenu) return;

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
                    // Nếu ở tầng 10, tiến lại gần vị trí Boss (cạnh phải) sẽ kích hoạt trận chiến 1 phút
                    if (isBossFloor && !bossFightStarted && newX >= 9) {
                        startCerberusBossFight();
                    }

                    let mIndex = monsters.findIndex(m => m.x === newX && m.y === newY);
                    if (mIndex !== -1) {
                        monsters[mIndex].hp -= player.damage;
                        player.score += 200;
                        slashEffect = { x: newX, y: newY, timer: 6 };
                        floatingTexts.push({ text: "-" + player.damage, x: newX * TILE_SIZE + 10, y: newY * TILE_SIZE, color: '#f1c40f', timer: 25 });

                        if (monsters[mIndex].hp <= 0) {
                            monsters.splice(mIndex, 1);
                            player.score += 500;
                        }
                    } else if (tile === 3) {
                        player.score += 600;
                        player.keys += 1;
                        player.hp = Math.min(player.maxHp, player.hp + 50);
                        currentMap[newY][newX] = 0;
                        floatingTexts.push({ text: "+50 HP", x: newX * TILE_SIZE, y: newY * TILE_SIZE, color: '#2ecc71', timer: 30 });
                    } else if (tile === 2) {
                        if (isBossFloor) {
                            if (!bossFightStarted) {
                                startCerberusBossFight();
                                return;
                            } else if (!bossDefeatedAnimation) {
                                alert("⚔️ Hãy chiến đấu sinh tồn với Chó 3 Đầu Cerberus đủ 1 phút để tung đòn kết liễu phá đảo!");
                                return;
                            }
                        } else {
                            if (player.floor >= 10) {
                                gameWon = true;
                                stopBGM();
                                drawGame();
                                return;
                            }
                            player.floor++;
                            player.score += 2000;
                            inTransitionMenu = true;
                            if (monsterMoveTimer) clearInterval(monsterMoveTimer);
                            drawGame();
                            return;
                        }
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

        function drawGame() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            if (gameWon) {
                ctx.fillStyle = '#0b0b0e';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = '#f1c40f';
                ctx.font = 'bold 28px "Courier New"';
                ctx.textAlign = 'center';
                ctx.fillText('👑 CHIẾN THẮNG - PHÁ ĐẢO! 👑', canvas.width / 2, 120);
                ctx.fillStyle = '#ffffff';
                ctx.font = 'bold 15px "Courier New"';
                ctx.fillText('Bạn đã đánh bại Chó 3 Đầu Cerberus sau 1 phút quyết chiến!', canvas.width / 2, 170);
                ctx.fillText('Đã vượt qua hoàn hảo cả 10 Tầng Hầm Ngục!', canvas.width / 2, 210);
                ctx.fillText('Điểm số cuối cùng: ' + player.score, canvas.width / 2, 250);
                ctx.fillStyle = '#2ecc71';
                ctx.fillText('Cảm ơn bạn đã giải cứu thế giới!', canvas.width / 2, 290);
                return;
            }

            // 1. Vẽ Map
            for (let r = 0; r < ROWS; r++) {
                for (let c = 0; c < COLS; c++) {
                    let x = c * TILE_SIZE;
                    let y = r * TILE_SIZE;

                    if (currentMap[r][c] === 1) {
                        ctx.fillStyle = isBossFloor ? '#4a1515' : (player.floor >= 4 ? '#1f4e5b' : '#2c223b');
                        ctx.fillRect(x, y, TILE_SIZE, TILE_SIZE);
                        ctx.fillStyle = isBossFloor ? '#922b21' : (player.floor >= 4 ? '#2874a6' : '#3e3154');
                        ctx.fillRect(x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4);
                    } else {
                        ctx.fillStyle = '#1b1726';
                        ctx.fillRect(x, y, TILE_SIZE, TILE_SIZE);
                        ctx.strokeStyle = '#252033';
                        ctx.strokeRect(x, y, TILE_SIZE, TILE_SIZE);
                    }

                    if (currentMap[r][c] === 2) {
                        ctx.fillStyle = isBossFloor ? '#e74c3c' : '#f1c40f';
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

            // 2. VẼ BOSS CHÓ 3 ĐẦU (CERBERUS) NẾU Ở TẦNG 10
            if (isBossFloor) {
                let bx = 11 * TILE_SIZE;
                let by = 4 * TILE_SIZE;

                if (!bossDefeatedAnimation) {
                    // Thân chính đồ sộ của Chó 3 Đầu
                    ctx.fillStyle = '#8b0000';
                    ctx.fillRect(bx, by + 10, 70, 50);
                    ctx.fillStyle = '#ff4500';
                    ctx.fillRect(bx + 10, by + 18, 50, 34);

                    // 3 Đầu chó hung tợn phun lửa
                    // Đầu trái
                    ctx.fillStyle = '#b22222';
                    ctx.fillRect(bx - 10, by, 25, 25);
                    ctx.fillStyle = '#ffff00'; // Mắt đỏ/vàng
                    ctx.fillRect(bx - 4, by + 6, 4, 4);
                    // Đầu giữa
                    ctx.fillStyle = '#b22222';
                    ctx.fillRect(bx + 22, by - 8, 25, 25);
                    ctx.fillStyle = '#ffff00';
                    ctx.fillRect(bx + 30, by - 2, 4, 4);
                    // Đầu phải
                    ctx.fillStyle = '#b22222';
                    ctx.fillRect(bx + 55, by, 25, 25);
                    ctx.fillStyle = '#ffff00';
                    ctx.fillRect(bx + 62, by + 6, 4, 4);

                    // Thanh máu Boss & Thời gian đếm ngược 1 phút
                    ctx.fillStyle = 'rgba(0,0,0,0.8)';
                    ctx.fillRect(canvas.width / 2 - 150, 15, 300, 30);
                    ctx.strokeStyle = '#e74c3c';
                    ctx.strokeRect(canvas.width / 2 - 150, 15, 300, 30);

                    ctx.fillStyle = '#e74c3c';
                    ctx.font = 'bold 12px "Courier New"';
                    ctx.textAlign = 'center';
                    let statusText = bossFightStarted ? ('🔥 DIỆT BOSS: ' + bossTimer + 's') : ('⚠️ LẠI GẦN ĐỂ ĐẤU CHÓ 3 ĐẦU!');
                    ctx.fillText(statusText, canvas.width / 2, 34);
                    ctx.textAlign = 'left';
                } else {
                    // Hiệu ứng bị nhân vật đâm chết
                    ctx.fillStyle = '#ffffff';
                    ctx.font = 'bold 20px "Courier New"';
                    ctx.textAlign = 'center';
                    ctx.fillText('💥 ĐÒN TẤT SÁT - CHÓ 3 ĐẦU GỤC NGÃ! 💥', canvas.width / 2, 80);
                    ctx.textAlign = 'left';
                }
            }

            // Quái thường ở tầng khác
            monsters.forEach(function(m) {
                let mx = m.x * TILE_SIZE;
                let my = m.y * TILE_SIZE;
                ctx.fillStyle = '#e67e22';
                ctx.fillRect(mx + 6, my + 4, 28, 30);
                ctx.fillStyle = '#000';
                ctx.fillRect(mx + 5, my + 2, 30, 4);
                ctx.fillStyle = '#e74c3c';
                ctx.fillRect(mx + 5, my + 2, Math.max(0, (m.hp / m.maxHp) * 30), 4);
            });

            // 3. Vết chém
            if (slashEffect && slashEffect.timer > 0) {
                let sx = slashEffect.x * TILE_SIZE;
                let sy = slashEffect.y * TILE_SIZE;
                ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(sx + 8, sy + 8); ctx.lineTo(sx + 32, sy + 32); ctx.stroke();
                slashEffect.timer--;
            }

            // 4. NHÂN VẬT CHÍNH (CÓ MẮT MŨI MIỆNG, NHÚN NHẢY, VŨ KHÍ CHUẨN TÊN)
            let px = player.x * TILE_SIZE;
            let bounce = Math.sin(idleCounter) * 2; 
            let py = (player.y * TILE_SIZE) + bounce;

            ctx.fillStyle = player.cloakColor;
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
            
            // Khuôn mặt: Mắt, mũi, miệng
            ctx.fillStyle = '#000000';
            ctx.fillRect(px + 12, py + 9, 2, 2);
            ctx.fillRect(px + 18, py + 9, 2, 2);
            ctx.fillStyle = '#f5b041';
            ctx.fillRect(px + 15, py + 11, 2, 2);
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(px + 14, py + 14, 4, 1);

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

            drawWeapon(px, py);

            // 5. Floating texts
            for (let i = floatingTexts.length - 1; i >= 0; i--) {
                let ft = floatingTexts[i];
                ctx.fillStyle = ft.color;
                ctx.font = 'bold 12px "Courier New"';
                ctx.fillText(ft.text, ft.x, ft.y);
                ft.y -= 0.8;
                ft.timer--;
                if (ft.timer <= 0) floatingTexts.splice(i, 1);
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
            ctx.fillText('FLOOR: ' + player.floor + '/10 F | KEYS: ' + player.keys, 20, 48);
            
            ctx.fillStyle = '#3498db';
            ctx.fillText('SCORE: ' + player.score, 20, 68);
            
            ctx.fillStyle = '#e67e22';
            ctx.fillText('ARMOR: ' + player.armorName, 20, 88);

            ctx.fillStyle = player.bladeColor;
            ctx.fillText('WEAPON: ' + player.weaponName, 20, 106);

            // --- 7. MENU CHUYỂN TẦNG ---
            if (inTransitionMenu) {
                ctx.fillStyle = 'rgba(0, 0, 0, 0.85)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = '#1a1824';
                ctx.fillRect(120, 70, 360, 260);
                ctx.strokeStyle = '#f1c40f';
                ctx.lineWidth = 3;
                ctx.strokeRect(120, 70, 360, 260);

                ctx.fillStyle = '#f1c40f';
                ctx.font = 'bold 18px "Courier New"';
                ctx.textAlign = 'center';
                ctx.fillText('⚡ HOÀN THÀNH TẦNG ' + (player.floor - 1) + ' ⚡', canvas.width / 2, 110);

                ctx.fillStyle = '#ffffff';
                ctx.font = '13px "Courier New"';
                ctx.fillText('Trang bị mới: ' + player.armorName, canvas.width / 2, 138);
                ctx.fillText('Vũ khí mới: ' + player.weaponName, canvas.width / 2, 162);
                ctx.fillText('Sát thương: ' + player.damage, canvas.width / 2, 186);

                ctx.fillStyle = '#2980b9';
                ctx.fillRect(100, 215, 180, 50);
                ctx.strokeStyle = '#3498db';
                ctx.strokeRect(100, 215, 180, 50);
                ctx.fillStyle = '#ffffff';
                ctx.font = 'bold 13px "Courier New"';
                ctx.fillText('⚔️ ĐỔI VŨ KHÍ', 190, 245);

                ctx.fillStyle = '#27ae60';
                ctx.fillRect(320, 215, 180, 50);
                ctx.strokeStyle = '#2ecc71';
                ctx.strokeRect(320, 215, 180, 50);
                ctx.fillStyle = '#ffffff';
                ctx.font = 'bold 13px "Courier New"';
                ctx.fillText('▶️ QUA TẦNG ' + player.floor, 410, 245);

                ctx.textAlign = 'left';
            }
        }

        gameLoop();
    </script>
</body>
</html>
"""

components.html(game_html, height=520)
