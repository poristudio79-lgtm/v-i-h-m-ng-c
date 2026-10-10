
      import streamlit as st
import streamlit.components.v1 as components

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Pixel Dungeon: Ultimate RPG",
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

st.markdown("<h1 class='main-title'>⚔️ PIXEL DUNGEON: ULTIMATE RPG 🗡️</h1>", unsafe_allow_html=True)
st.markdown("<div class='instructions'>Dùng phím <b>W, A, S, D</b> để di chuyển. Hình dáng vũ khí khớp chuẩn tên gọi (Excalibur, Thương, Rìu, Dao...), nhân vật có mắt mũi miệng, qua màn có Menu giữa màn hình! Phá đảo ở Tầng 10!</div>", unsafe_allow_html=True)

game_html = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Pixel Dungeon Complete</title>
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
            hp: 150,
            maxHp: 150,
            score: 0,
            floor: 1,
            keys: 0,
            armorName: "",
            cloakColor: "",
            armorColor: "",
            helmetColor: "",
            featherColor: "",
            weaponName: "",
            weaponType: "sword", // sword, spear, axe, bow, dagger, excalibur
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
        
        let idleCounter = 0;
        let slashEffect = null;
        let floatingTexts = [];

        // --- HỆ THỐNG ÂM THANH CHIPTUNE 8-BIT ---
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

        // --- 10 TẦNG VỚI TRANG BỊ VÀ LOẠI VŨ KHÍ CHUẨN XÁC ---
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

        // Danh sách vũ khí khi bấm nút "Đổi vũ khí" trong menu chuyển tầng
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

        // --- HÀM VẼ HÌNH DÁNG VŨ KHÍ CHUẨN XÁC THEO TÊN ---
        function drawWeapon(px, py) {
            let type = player.weaponType;

            if (type === "dagger") {
                // Dao găm ngắn, nhỏ gọn
                ctx.fillStyle = player.pommelColor;
                ctx.fillRect(px + 28, py + 25, 3, 2);
                ctx.fillStyle = player.hiltColor;
                ctx.fillRect(px + 28, py + 21, 3, 4);
                ctx.fillStyle = player.guardColor;
                ctx.fillRect(px + 26, py + 19, 7, 2);
                ctx.fillStyle = player.bladeColor;
                ctx.fillRect(px + 28, py + 13, 3, 6);
                ctx.fillStyle = player.tipColor;
                ctx.beginPath();
                ctx.moveTo(px + 28, py + 13);
                ctx.lineTo(px + 29.5, py + 9);
                ctx.lineTo(px + 31, py + 13);
                ctx.fill();

            } else if (type === "spear") {
                // Cán thương dài, mũi thương nhọn hoắt
                ctx.fillStyle = player.pommelColor;
                ctx.fillRect(px + 28, py + 30, 4, 3);
                ctx.fillStyle = player.hiltColor;
                ctx.fillRect(px + 28, py + 12, 4, 18);
                ctx.fillStyle = player.guardColor;
                ctx.fillRect(px + 26, py + 10, 8, 2);
                ctx.fillStyle = player.bladeColor;
                ctx.beginPath();
                ctx.moveTo(px + 25, py + 10);
                ctx.lineTo(px + 30, py - 6);
                ctx.lineTo(px + 35, py + 10);
                ctx.fill();
                ctx.fillStyle = player.tipColor;
                ctx.beginPath();
                ctx.moveTo(px + 28, py + 4);
                ctx.lineTo(px + 30, py - 6);
                ctx.lineTo(px + 32, py + 4);
                ctx.fill();

            } else if (type === "axe") {
                // Rìu chiến
                ctx.fillStyle = player.hiltColor;
                ctx.fillRect(px + 28, py + 10, 4, 18);
                ctx.fillStyle = player.pommelColor;
                ctx.fillRect(px + 28, py + 27, 4, 3);
                ctx.fillStyle = player.bladeColor;
                ctx.beginPath();
                ctx.moveTo(px + 30, py + 10);
                ctx.lineTo(px + 40, py + 4);
                ctx.lineTo(px + 40, py + 20);
                ctx.lineTo(px + 30, py + 16);
                ctx.fill();
                ctx.fillStyle = player.tipColor;
                ctx.fillRect(px + 39, py + 5, 2, 14);

            } else if (type === "bow") {
                // Cung tên
                ctx.strokeStyle = player.hiltColor;
                ctx.lineWidth = 3;
                ctx.beginPath();
                ctx.arc(px + 26, py + 16, 12, -Math.PI / 2, Math.PI / 2, false);
                ctx.stroke();
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(px + 26, py + 4);
                ctx.lineTo(px + 26, py + 28);
                ctx.stroke();
                ctx.fillStyle = player.tipColor;
                ctx.fillRect(px + 22, py + 15, 12, 2);

            } else if (type === "excalibur") {
                // Kiếm Thần Excalibur tối thượng rực rỡ
                ctx.fillStyle = "#f1c40f";
                ctx.fillRect(px + 27, py + 28, 6, 4);
                ctx.fillStyle = player.hiltColor;
                ctx.fillRect(px + 28, py + 20, 4, 8);
                ctx.fillStyle = player.guardColor;
                ctx.fillRect(px + 22, py + 17, 16, 4);
                ctx.fillStyle = "#f39c12";
                ctx.fillRect(px + 24, py + 15, 12, 2);
                ctx.fillStyle = player.bladeColor;
                ctx.fillRect(px + 27, py - 2, 6, 19);
                ctx.fillStyle = player.tipColor;
                ctx.beginPath();
                ctx.moveTo(px + 27, py - 2);
                ctx.lineTo(px + 30, py - 10);
                ctx.lineTo(px + 33, py - 2);
                ctx.fill();

            } else {
                // Kiếm tiêu chuẩn (Sword)
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
            }
        }

        // --- 10 TẦNG MAP ---
        function loadFloor(floorNum) {
            player.x = 1;
            player.y = 1;
            updatePlayerGear(floorNum);

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
                monsters = [{ x: 12, y: 5, hp: 40, maxHp: 40, type: 'slime' }, { x: 6, y: 3, hp: 35, maxHp: 35, type: 'bat' }];
            } else if (floorNum === 2) {
                currentMap = [
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                    [1,0,1,0,0,0,1,0,0,0,3,0,0,2,1],
                    [1,0,1,1,1,0,1,0,1,1,1,1,1,0,1],
                    [1,0,0,0,1,0,0,0,1,0,0,0,1,0,1],
                    [1,1,1,0,1,1,1,0,1,0,1,0,1,0,1],
                    [1,3,0,0,0,0,1,0,0,0,1,0,0,0,1],
                    [1,0,1,1,1,0,1,1,1,1,1,1,1,0,1],
                    [1,0,0,0,1,0,0,0,0,0,0,0,1,3,1],
                    [1,1,1,0,3,1,1,1,1,1,1,0,0,0,1],
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
                ];
                exitCoord = { x: 13, y: 1 };
                monsters = [{ x: 7, y: 3, hp: 60, maxHp: 60, type: 'goblin' }, { x: 3, y: 5, hp: 55, maxHp: 55, type: 'spider' }];
            } else if (floorNum === 3) {
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
                monsters = [{ x: 7, y: 4, hp: 80, maxHp: 80, type: 'golem' }, { x: 3, y: 1, hp: 70, maxHp: 70, type: 'demon' }];
            } else if (floorNum === 4) {
                currentMap = [
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                    [1,0,1,1,0,0,0,0,0,1,1,1,3,2,1],
                    [1,0,1,1,0,1,1,1,0,1,1,1,0,0,1],
                    [1,0,0,0,0,1,3,1,0,0,0,0,0,1,1],
                    [1,1,1,0,1,1,0,1,1,0,1,1,0,1,1],
                    [1,3,0,0,0,0,0,0,0,0,0,1,0,0,1],
                    [1,1,1,0,1,1,0,1,1,0,1,1,1,0,1],
                    [1,0,0,0,1,1,0,1,1,0,1,3,0,0,1],
                    [1,0,1,1,1,1,0,1,1,0,1,1,1,0,1],
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
                ];
                exitCoord = { x: 13, y: 1 };
                monsters = [{ x: 6, y: 5, hp: 100, maxHp: 100, type: 'goblin' }, { x: 12, y: 7, hp: 90, maxHp: 90, type: 'demon' }];
            } else if (floorNum === 5) {
                currentMap = [
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                    [1,0,0,0,1,3,0,0,0,3,1,0,0,2,1],
                    [1,0,1,0,1,1,1,0,1,1,1,0,1,0,1],
                    [1,0,1,0,0,0,0,0,0,0,0,0,1,0,1],
                    [1,0,1,1,1,0,1,1,1,0,1,1,1,0,1],
                    [1,0,0,0,0,0,1,3,1,0,0,0,0,0,1],
                    [1,1,1,0,1,1,1,0,1,1,1,0,1,1,1],
                    [1,3,0,0,0,0,0,0,0,0,0,0,3,0,1],
                    [1,0,1,1,1,0,1,1,1,0,1,1,1,0,1],
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
                ];
                exitCoord = { x: 13, y: 1 };
                monsters = [{ x: 7, y: 3, hp: 120, maxHp: 120, type: 'golem' }, { x: 3, y: 7, hp: 110, maxHp: 110, type: 'demon' }];
            } else if (floorNum === 6) {
                currentMap = [
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                    [1,0,1,0,0,0,0,1,0,0,0,0,1,2,1],
                    [1,0,1,1,1,1,0,1,0,1,1,1,1,0,1],
                    [1,0,0,0,0,1,0,0,0,1,3,0,0,0,1],
                    [1,1,1,0,1,1,1,1,0,1,1,1,1,0,1],
                    [1,3,0,0,0,0,3,1,0,0,0,0,1,0,1],
                    [1,1,1,0,1,1,1,1,0,1,1,0,1,0,1],
                    [1,0,0,0,0,0,0,0,0,1,1,0,0,3,1],
                    [1,0,1,1,1,1,1,1,1,1,1,1,1,0,1],
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
                ];
                exitCoord = { x: 13, y: 1 };
                monsters = [{ x: 5, y: 3, hp: 140, maxHp: 140, type: 'demon' }, { x: 8, y: 7, hp: 130, maxHp: 130, type: 'golem' }];
            } else if (floorNum === 7) {
                currentMap = [
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                    [1,0,0,0,1,3,0,1,0,3,1,0,0,2,1],
                    [1,0,1,0,1,1,0,1,0,1,1,0,1,0,1],
                    [1,0,1,0,0,0,0,0,0,0,0,0,1,0,1],
                    [1,0,1,1,1,0,1,1,1,0,1,1,1,0,1],
                    [1,0,0,0,0,0,1,0,1,0,0,0,0,0,1],
                    [1,1,1,0,1,1,1,0,1,1,1,0,1,1,1],
                    [1,3,0,0,0,0,0,0,0,0,0,0,3,0,1],
                    [1,0,1,1,1,0,1,1,1,0,1,1,1,0,1],
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
                ];
                exitCoord = { x: 13, y: 1 };
                monsters = [{ x: 6, y: 5, hp: 160, maxHp: 160, type: 'demon' }, { x: 12, y: 7, hp: 150, maxHp: 150, type: 'golem' }];
            } else if (floorNum === 8) {
                currentMap = [
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                    [1,0,1,0,0,0,1,0,0,0,1,3,0,2,1],
                    [1,0,1,1,1,0,1,0,1,1,1,1,1,0,1],
                    [1,0,0,0,1,0,0,0,1,0,0,0,1,0,1],
                    [1,1,1,0,1,1,1,0,1,0,1,0,1,0,1],
                    [1,3,0,0,0,0,1,0,0,0,1,0,0,3,1],
                    [1,0,1,1,1,0,1,1,1,1,1,1,1,0,1],
                    [1,0,0,0,1,0,0,0,0,0,0,0,1,0,1],
                    [1,1,1,0,3,1,1,1,1,1,1,0,0,0,1],
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
                ];
                exitCoord = { x: 13, y: 1 };
                monsters = [{ x: 7, y: 3, hp: 180, maxHp: 180, type: 'demon' }, { x: 3, y: 5, hp: 170, maxHp: 170, type: 'golem' }];
            } else if (floorNum === 9) {
                currentMap = [
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                    [1,0,0,0,0,0,0,3,0,0,0,0,1,2,1],
                    [1,0,1,1,1,1,0,1,0,1,1,1,1,0,1],
                    [1,0,1,3,0,0,0,1,0,0,0,3,1,0,1],
                    [1,0,1,0,1,1,1,1,1,1,0,1,1,0,1],
