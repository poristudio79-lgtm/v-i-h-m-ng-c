import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Pixel Dungeon: Arena Edition",
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

st.markdown("<h1 class='main-title'>⚔️ PIXEL DUNGEON: BÌNH NGUYÊN VÔ TẬN 🗡️</h1>", unsafe_allow_html=True)
st.markdown("<div class='instructions'>Dùng phím <b>W, A, S, D</b> để di chuyển. Đã loại bỏ menu đổi vũ khí. Bật nhạc để nghe giai điệu chiến trận Liên Quân! Tầng 10 đụng độ Trùm <b>SỨA LỬA</b>!</div>", unsafe_allow_html=True)

game_html = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Pixel Dungeon Liên Quân</title>
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
    <button id="audio-btn" onclick="toggleAudio()">🔥 Bật / Tắt Nhạc Liên Quân Mobile</button>

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
        let boss = null;
        let exitCoord = { x: 13, y: 8 };
        let monsterMoveTimer = null;
        let gameWon = false;
        
        let bossDefeatedAnimation = false;
        let jumpAttackAnim = 0;
        let showBossAlert = false;

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
                startArenaThemeBGM();
                isPlayingBGM = true;
                document.getElementById("audio-btn").innerText = "🔇 Tắt Nhạc Liên Quân Mobile";
            } else {
                stopBGM();
                isPlayingBGM = false;
                document.getElementById("audio-btn").innerText = "🔥 Bật / Tắt Nhạc Liên Quân Mobile";
            }
        }

        // Nhạc nền Anthem Arena (Liên Quân) cực hào hùng khi mới bắt đầu
        function startArenaThemeBGM() {
            const arenaNotes = [
                220.00, 293.66, 329.63, 349.23, 293.66, 440.00, 392.00, 349.23,
                329.63, 293.66, 261.63, 220.00, 293.66, 349.23, 329.63, 293.66
            ];
            let noteIndex = 0;

            bgmInterval = setInterval(function() {
                if (!isPlayingBGM || !audioCtx) return;
                let osc = audioCtx.createOscillator();
                let gain = audioCtx.createGain();

                // Dùng sóng square/triangle mô phỏng tiếng kèn đồng & giai điệu chiến đấu
                osc.type = (noteIndex % 4 === 0) ? 'triangle' : 'square';
                osc.frequency.setValueAtTime(arenaNotes[noteIndex], audioCtx.currentTime);

                gain.gain.setValueAtTime(0.05, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.18);

                osc.connect(gain);
                gain.connect(audioCtx.destination);

                osc.start();
                osc.stop(audioCtx.currentTime + 0.20);

                noteIndex = (noteIndex + 1) % arenaNotes.length;
            }, 160);
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

        const mapsDatabase = {
            1: [
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
            ],
            2: [
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
            ],
            3: [
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
            ],
            4: [
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
            ],
            5: [
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
            ],
            6: [
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
            ],
            7: [
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
            ],
            8: [
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
            ],
            9: [
                [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                [1,0,0,0,0,0,0,3,0,0,0,0,1,2,1],
                [1,0,1,1,1,1,0,1,0,1,1,1,1,0,1],
                [1,0,1,3,0,0,0,1,0,0,0,3,1,0,1],
                [1,0,1,0,1,1,1,1,1,1,0,1,1,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,1,1,1,1,1,0,1,1,1,1,1,1,0,1],
                [1,3,0,0,0,0,0,0,0,0,0,0,3,0,1],
                [1,0,1,1,1,1,1,1,1,1,1,1,1,0,1],
                [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
            ],
            10: [
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
            ]
        };

        const monstersDatabase = {
            1: [{ x: 12, y: 5, hp: 40, maxHp: 40, type: 'slime' }, { x: 6, y: 3, hp: 35, maxHp: 35, type: 'bat' }],
            2: [{ x: 7, y: 3, hp: 60, maxHp: 60, type: 'goblin' }, { x: 3, y: 5, hp: 55, maxHp: 55, type: 'spider' }],
            3: [{ x: 7, y: 4, hp: 80, maxHp: 80, type: 'golem' }, { x: 3, y: 1, hp: 70, maxHp: 70, type: 'demon' }],
            4: [{ x: 6, y: 5, hp: 100, maxHp: 100, type: 'goblin' }, { x: 12, y: 7, hp: 90, maxHp: 90, type: 'demon' }],
            5: [{ x: 7, y: 3, hp: 120, maxHp: 120, type: 'golem' }, { x: 3, y: 7, hp: 110, maxHp: 110, type: 'demon' }],
            6: [{ x: 5, y: 3, hp: 140, maxHp: 140, type: 'demon' }, { x: 8, y: 7, hp: 130, maxHp: 130, type: 'golem' }],
            7: [{ x: 6, y: 5, hp: 160, maxHp: 160, type: 'demon' }, { x: 12, y: 7, hp: 150, maxHp: 150, type: 'golem' }],
            8: [{ x: 7, y: 3, hp: 180, maxHp: 180, type: 'demon' }, { x: 3, y: 5, hp: 170, maxHp: 170, type: 'golem' }],
            9: [{ x: 7, y: 4, hp: 200, maxHp: 200, type: 'demon' }, { x: 3, y: 1, hp: 190, maxHp: 190, type: 'demon' }],
            10: []
        };

        function loadFloor(floorNum) {
            player.x = 1;
            player.y = 1;
            updatePlayerGear(floorNum);
            bossDefeatedAnimation = false;
            jumpAttackAnim = 0;
            boss = null;

            currentMap = JSON.parse(JSON.stringify(mapsDatabase[floorNum] || mapsDatabase[1]));

            if (floorNum === 10) {
                exitCoord = { x: 13, y: 8 };
                monsters = [];
                boss = { x: 11, y: 4, hp: 1800, maxHp: 1800, type: 'fire_jellyfish' };
                
                showBossAlert = true;
                setTimeout(function() {
                    showBossAlert = false;
                }, 3500);

            } else {
                exitCoord = { x: 13, y: 1 };
                monsters = JSON.parse(JSON.stringify(monstersDatabase[floorNum] || monstersDatabase[1]));
            }
            currentMap[exitCoord.y][exitCoord.x] = 2;
        }

        loadFloor(1);

        function startMonsterAI() {
            if (monsterMoveTimer) clearInterval(monsterMoveTimer);

            monsterMoveTimer = setInterval(function() {
                if (gameWon) return;

                if (player.floor === 10 && boss && boss.hp > 0) {
                    let possibleMoves = [];
                    let directions = [{ x: 0, y: -1 }, { x: 0, y: 1 }, { x: -1, y: 0 }, { x: 1, y: 0 }];

                    directions.forEach(function(d) {
                        let nextX = boss.x + d.x;
                        let nextY = boss.y + d.y;
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
                        boss.x = possibleMoves[0].x;
                        boss.y = possibleMoves[0].y;
                    }

                    if (Math.abs(boss.x - player.x) + Math.abs(boss.y - player.y) <= 1) {
                        let bossDmg = 25;
                        player.hp -= bossDmg;
                        floatingTexts.push({ text: "-" + bossDmg, x: player.x * TILE_SIZE + 10, y: player.y * TILE_SIZE, color: '#e74c3c', timer: 25 });
                        if (player.hp <= 0) {
                            alert("💀 TRÙM SỨA LỬA ĐÃ THIÊU RỤI BẠN!");
                            player.hp = 200;
                            player.floor = 1;
                            loadFloor(1);
                        }
                    }
                }

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
                            player.hp = 200;
                            player.floor = 1;
                            loadFloor(1);
                        }
                    }
                });

                drawGame();
            }, 1100);
        }

        startMonsterAI();

        window.addEventListener('keydown', function(e) {
            if (gameWon) return;

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
                    if (boss && boss.hp > 0 && boss.x === newX && boss.y === newY) {
                        boss.hp -= player.damage;
                        player.score += 300;
                        slashEffect = { x: newX, y: newY, timer: 6 };
                        floatingTexts.push({ text: "-" + player.damage, x: newX * TILE_SIZE + 10, y: newY * TILE_SIZE, color: '#f1c40f', timer: 25 });

                        if (boss.hp <= 0) {
                            bossDefeatedAnimation = true;
                            jumpAttackAnim = 30;
                        }
                        return;
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
                        if (player.floor >= 10) {
                            if (boss && boss.hp > 0) {
                                alert("⚔️ Hãy tiêu diệt TRÙM SỨA LỬA trước khi mở cửa thoát hiểm!");
                                return;
                            }
                            gameWon = true;
                            stopBGM();
                            drawGame();
                            return;
                        }
                        // CHUYỂN THẲNG QUA TẦNG MỚI (ĐÃ BỎ MỤC ĐỔI VŨ KHÍ)
                        player.floor++;
                        player.score += 2000;
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
            if (jumpAttackAnim > 0) jumpAttackAnim--;
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
                ctx.fillText('Chào mừng bạn đến với Bình Nguyên Vô Tận vinh quang!', canvas.width / 2, 170);
                ctx.fillText('Đã vượt qua hoàn hảo cả 10 Tầng Hầm Ngục!', canvas.width / 2, 210);
                ctx.fillText('Điểm số cuối cùng: ' + player.score, canvas.width / 2, 250);
                ctx.fillStyle = '#2ecc71';
                ctx.fillText('Cảm ơn bạn đã giải cứu thế giới!', canvas.width / 2, 290);
                return;
            }

            for (let r = 0; r < ROWS; r++) {
                for (let c = 0; c < COLS; c++) {
                    let x = c * TILE_SIZE;
                    let y = r * TILE_SIZE;

                    if (currentMap[r][c] === 1) {
                        ctx.fillStyle = player.floor === 10 ? '#4a1515' : (player.floor >= 6 ? '#1a252f' : '#2c223b');
                        ctx.fillRect(x, y, TILE_SIZE, TILE_SIZE);
                        ctx.fillStyle = player.floor === 10 ? '#922b21' : (player.floor >= 6 ? '#2c3e50' : '#3e3154');
                        ctx.fillRect(x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4);
                    } else {
                        ctx.fillStyle = '#1b1726';
                        ctx.fillRect(x, y, TILE_SIZE, TILE_SIZE);
                        ctx.strokeStyle = '#252033';
                        ctx.strokeRect(x, y, TILE_SIZE, TILE_SIZE);
                    }

                    if (currentMap[r][c] === 2) {
                        ctx.fillStyle = (player.floor === 10 && boss && boss.hp > 0) ? '#555555' : '#f1c40f';
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

            if (boss && boss.hp > 0) {
                let bx = boss.x * TILE_SIZE;
                let by = boss.y * TILE_SIZE;

                let pulse = Math.sin(idleCounter * 4) * 3;
                ctx.fillStyle = '#ff3300';
                ctx.beginPath();
                ctx.arc(bx + 20, by + 16, 16 + pulse, Math.PI, 0, false);
                ctx.fill();

                ctx.fillStyle = '#ff9900';
                ctx.beginPath();
                ctx.arc(bx + 20, by + 16, 10, Math.PI, 0, false);
                ctx.fill();

                ctx.fillStyle = '#ffffff';
                ctx.fillRect(bx + 12, by + 10, 4, 4);
                ctx.fillRect(bx + 24, by + 10, 4, 4);
                ctx.fillStyle = '#000000';
                ctx.fillRect(bx + 14, by + 12, 2, 2);
                ctx.fillRect(bx + 26, by + 12, 2, 2);

                ctx.strokeStyle = '#e74c3c';
                ctx.lineWidth = 3;
                for (let i = 0; i < 5; i++) {
                    let wave = Math.sin(idleCounter * 5 + i) * 4;
                    ctx.beginPath();
                    ctx.moveTo(bx + 8 + i * 6, by + 16);
                    ctx.lineTo(bx + 8 + i * 6 + wave, by + 36);
                    ctx.stroke();
                }

                ctx.fillStyle = '#000';
                ctx.fillRect(bx, by - 8, 40, 5);
                ctx.fillStyle = '#e74c3c';
                ctx.fillRect(bx, by - 8, Math.max(0, (boss.hp / boss.maxHp) * 40), 5);
            } else if (bossDefeatedAnimation) {
                let bx = 11 * TILE_SIZE;
                let by = 4 * TILE_SIZE;
                ctx.fillStyle = '#440000';
                ctx.fillRect(bx + 4, by + 15, 32, 15);
                ctx.fillStyle = '#f1c40f';
                ctx.font = 'bold 12px "Courier New"';
                ctx.fillText('💥 SỨA LỬA GỤC NGÃ!', bx - 20, by - 5);
            }

            monsters.forEach(function(m) {
                let mx = m.x * TILE_SIZE;
                let my = m.y * TILE_SIZE;

                if (m.type === 'slime') {
                    ctx.fillStyle = '#2ecc71'; ctx.beginPath(); ctx.arc(mx + 20, my + 25, 12, Math.PI, 0, false); ctx.fill();
                } else if (m.type === 'bat') {
                    ctx.fillStyle = '#9b59b6'; ctx.fillRect(mx + 10, my + 15, 20, 10);
                } else if (m.type === 'goblin') {
                    ctx.fillStyle = '#e67e22'; ctx.fillRect(mx + 12, my + 10, 16, 20);
                } else if (m.type === 'spider') {
                    ctx.fillStyle = '#34495e'; ctx.fillRect(mx + 10, my + 12, 20, 14);
                } else {
                    ctx.fillStyle = '#c0392b'; ctx.fillRect(mx + 6, my + 4, 28, 30);
                }

                ctx.fillStyle = '#000';
                ctx.fillRect(mx + 5, my + 2, 30, 4);
                ctx.fillStyle = '#e74c3c';
                ctx.fillRect(mx + 5, my + 2, Math.max(0, (m.hp / m.maxHp) * 30), 4);
            });

            if (slashEffect && slashEffect.timer > 0) {
                let sx = slashEffect.x * TILE_SIZE;
                let sy = slashEffect.y * TILE_SIZE;
                ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(sx + 8, sy + 8); ctx.lineTo(sx + 32, sy + 32); ctx.stroke();
                slashEffect.timer--;
            }

            let px = player.x * TILE_SIZE;
            let bounce = Math.sin(idleCounter) * 2; 
            let py = (player.y * TILE_SIZE) + bounce;

            if (jumpAttackAnim > 0) {
                py -= Math.sin((30 - jumpAttackAnim) / 30 * Math.PI) * 35;
            }

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

            for (let i = floatingTexts.length - 1; i >= 0; i--) {
                let ft = floatingTexts[i];
                ctx.fillStyle = ft.color;
                ctx.font = 'bold 12px "Courier New"';
                ctx.fillText(ft.text, ft.x, ft.y);
                ft.y -= 0.8;
                ft.timer--;
                if (ft.timer <= 0) floatingTexts.splice(i, 1);
            }

            ctx.fillStyle = 'rgba(15, 15, 25, 0.65)';
            ctx.fillRect(10, 10, 260, 115);
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
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

            if (showBossAlert) {
                ctx.fillStyle = 'rgba(0, 0, 0, 0.88)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = '#1a1824';
                ctx.fillRect(80, 110, 440, 180);
                ctx.strokeStyle = '#e74c3c';
                ctx.lineWidth = 4;
                ctx.strokeRect(80, 110, 440, 180);

                ctx.fillStyle = '#e74c3c';
                ctx.font = 'bold 20px "Courier New"';
                ctx.textAlign = 'center';
                ctx.fillText('⚠️ BÌNH NGUYÊN VÔ TẬN ⚠️', canvas.width / 2, 155);

                ctx.fillStyle = '#ffffff';
                ctx.font = 'bold 14px "Courier New"';
                ctx.fillText('TRÙM CUỐI SỨA LỬA ĐÃ XUẤT HIỆN!', canvas.width / 2, 195);

                ctx.fillStyle = '#f1c40f';
                ctx.font = '13px "Courier New"';
                ctx.fillText('Hãy tiêu diệt nó để mở cánh cửa vinh quang!', canvas.width / 2, 235);

                ctx.textAlign = 'left';
            }
        }

        gameLoop();
    </script>
</body>
</html>
"""

components.html(game_html, height=520)
