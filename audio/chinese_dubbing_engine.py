"""Chinese Livestream & Clip Dubbing Engine for NeuralClips.

Detects Chinese/CJK gaming streams, generates context-aware high-energy Hindi voiceovers,
synthesizes natural neural speech (Edge-TTS hi-IN-MadhurNeural), generates synchronized
animated ASS subtitles with word-by-word highlighting, and formats viral localized metadata.
"""

import asyncio
import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.logging_config import setup_logger
from ai.transcript_engine import TranscriptEngine
from rendering.caption_engine import CaptionEngine

logger = setup_logger("neuralclips.chinese_dubbing")

# Regex pattern matching CJK Unified Ideographs (Hanzi / Chinese characters)
CHINESE_CHAR_PATTERN = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf]")

# Common Chinese gaming streamer / platform keywords
CHINESE_KEYWORDS = [
    "bilibili", "douyu", "huya", "chinese", "taiwan", "hong kong",
    "中文", "直播", "解说", "主播", "游侠", "游戏", "老番茄", "周淑怡",
    "gta6中文", "俠盜獵車手", "侠盗猎车手", "小智", "大司马", "旭旭宝宝"
]

# Viral Hindi commentary templates mapped to gameplay categories
HINDI_DUBBING_SCRIPTS = {
    "police_chase": {
        "hindi": "भाई साहब देखो! GTA 6 में 5-स्टार पुलिस चेस शुरू हो चुका है! पुलिस गाड़ियां पीछे पड़ी हैं, लेकिन भाई ने क्या कट मारा यार, बाल-बाल बच गया!",
        "hinglish": "BHAI SAHAB DEKHO! GTA 6 MEIN 5-STAR POLICE CHASE! KYA CUT MARA YAAR, BAAL BAAL BACH GAYA! 🚓🔥",
        "title": "GTA 6 Mein 5-Star Police Chase! Bro Escaped Like A Legend 🚓💀",
    },
    "funny_reaction": {
        "hindi": "अरे भाई ये क्या हो गया! गाड़ी सीधे खंभे से टकराई और आसमान में उड़ गई! भाई के तो होश ही उड़ गए, ऐसा रिएक्शन कभी नहीं देखा भाई!",
        "hinglish": "BHAI YE KYA HO GAYA! GAADI AASMAAN MEIN UD GAYI! BRO WAS NOT READY FOR THIS PHYSICS! 😂💀",
        "title": "When Chinese Streamer Realized GTA 6 Physics Are Broken 😂💀",
    },
    "high_skill_play": {
        "hindi": "अरे भाई की ड्राइविंग स्किल तो देखो! इतनी भारी ट्रैफिक में 200 की स्पीड से निकाल लिया! पूरे गेम में इसका कोई मुकाबला नहीं है भाई!",
        "hinglish": "BHAI KI DRIVING TO DEKHO! 200 KI SPEED PE NIKAL LIYA! UNREAL DRIVING MECHANICS! 🏎️💨",
        "title": "Fastest GTA 6 Driver In The World?! Impossible Driving 🏎️💨",
    },
    "stunt": {
        "hindi": "भाई साहब! बाइक से सीधे पुल के ऊपर से छलांग लगा दी! और लैंडिंग देखो भाई, एक खरोंच तक नहीं आई! एकदम गॉड-लेवल स्टंट!",
        "hinglish": "BHAI SAHAB! MOTORCYCLE SE PUL SE CHHALAANG! INSANE 1-IN-A-MILLION STUNT! 🏍️🚀",
        "title": "He Jumped Off The Tallest Bridge In GTA 6! 1-In-A-Million Stunt 🏍️🚀",
    },
    "clutch": {
        "hindi": "सिर्फ 1 HP बचा था भाई! चारों तरफ से गोलियां चल रही हैं, लेकिन भाई ने पलट कर जो हेडशॉट मारा, पूरा गेम पलट दिया भाई ने!",
        "hinglish": "SIRF 1 HP BACHA THA! CHARON TARAF SE FIRE, PHIR BHI CLUTCH KAR DIYA! UNBELIEVABLE 1 HP VICTORY! 🏆💥",
        "title": "He Had 1 HP In GTA 6... UNTIL HE PULLED OFF THIS CLUTCH 🏆🤯",
    },
    "rare_event": {
        "hindi": "अरे भाई ये GTA 6 में सीक्रेट ईस्टर एग मिल गया! पानी के अंदर ये क्या चमक रहा है भाई? ऐसा नजारा पहले कभी किसी ने नहीं देखा!",
        "hinglish": "BHAI SECRET EASTER EGG MIL GAYA! UNDERWATER MYSTERY IN GTA 6! SECRET REVEALED! 🦈😱",
        "title": "Secret Underwater Easter Egg Found In GTA 6! 😱🦈",
    },
    "unexpected_failure": {
        "hindi": "भाई हेलीकॉप्टर चुरा तो लिया, लेकिन 2 सेकंड में क्रेन से टकरा के ब्लास्ट हो गया! भाई का दिमाग ही खराब हो गया यार!",
        "hinglish": "HELICOPTER CHURA TO LIYA, LEKIN CRANE SE TAKRA KE BLAST HO GAYA! INSTANT REGRET! 🚁💥",
        "title": "He Stole A Helicopter In GTA 6 And Crashed It Immediately 🚁💥",
    },
    "default": {
        "hindi": "भाई साहब! GTA 6 का ये गेमप्ले सच में रोंगटे खड़े कर देने वाला है! देखो कैसे एक के बाद एक बवाल मोमेंट्स हो रहे हैं!",
        "hinglish": "BHAI SAHAB! GTA 6 KA CRAZIEST GAMEPLAY MOMENT! DEKHO KYA SCENE HUA HAI! 🔥🎮",
        "title": "Craziest GTA 6 Gameplay Moment You Will See Today! 🔥🎮",
    }
}


class ChineseDubbingEngine:
    """Detects Chinese content, translates & dubs into energetic Hindi with subtitles."""

    def __init__(self, voice: str = "hi-IN-MadhurNeural", rate: str = "+12%"):
        self.voice = voice
        self.rate = rate
        self.caption_engine = CaptionEngine()

    @staticmethod
    def is_chinese_content(
        title: str = "",
        channel_title: str = "",
        description: str = "",
        transcript: str = "",
    ) -> bool:
        """Determines if a video or livestream is Chinese based on text, title, or channel."""
        combined_text = f"{title} {channel_title} {description} {transcript}".lower()

        # Check for Chinese Hanzi characters
        if CHINESE_CHAR_PATTERN.search(combined_text):
            return True

        # Check for Chinese platform and creator keywords
        for kw in CHINESE_KEYWORDS:
            if kw in combined_text:
                return True

        return False

    def select_script(self, category: str = "", title: str = "") -> Dict[str, str]:
        """Selects the best matching high-energy Hindi dubbing script and subtitles."""
        title_lower = title.lower()

        # Keyword-based category refinement (Prioritize specific reaction/crash/glitch events first)
        if any(w in title_lower for w in ["funny", "laugh", "fail", "physics", "crash", "glitch", "broke"]):
            cat_key = "funny_reaction"
        elif any(w in title_lower for w in ["police", "chase", "cop", "5-star", "wanted", "busted", "swat"]):
            cat_key = "police_chase"
        elif any(w in title_lower for w in ["stunt", "jump", "fly", "skyscraper", "bridge", "motorcycle", "bike"]):
            cat_key = "stunt"
        elif any(w in title_lower for w in ["secret", "easter egg", "mystery", "underwater", "found"]):
            cat_key = "rare_event"
        elif any(w in title_lower for w in ["clutch", "1 hp", "win", "victory"]):
            cat_key = "clutch"
        elif any(w in title_lower for w in ["drive", "speed", "fast", "car", "supercar", "drift"]):
            cat_key = "high_skill_play"
        else:
            cat_key = category if category in HINDI_DUBBING_SCRIPTS else "default"

        return HINDI_DUBBING_SCRIPTS.get(cat_key, HINDI_DUBBING_SCRIPTS["default"])

    async def _generate_audio_async(self, text: str, output_path: str):
        """Asynchronously synthesizes speech using edge-tts."""
        import edge_tts
        tts = edge_tts.Communicate(text, voice=self.voice, rate=self.rate)
        await tts.save(output_path)

    def synthesize_hindi_audio(self, text: str, output_path: str) -> Optional[str]:
        """Synthesizes high-energy Hindi voiceover audio using neural TTS."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        try:
            asyncio.run(self._generate_audio_async(text, output_path))
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                logger.info(f"Synthesized neural Hindi voiceover: {output_path} ({os.path.getsize(output_path)} bytes)")
                return output_path
        except Exception as e:
            logger.error(f"Failed synthesizing Hindi dubbing with edge-tts: {e}")
        return None

    def generate_animated_subtitles(
        self,
        caption_text: str,
        output_ass_path: str,
        duration: float,
        words_per_line: int = 3,
    ) -> str:
        """Generates synchronized ASS subtitles with active word highlighting for mobile retention."""
        timed_words = TranscriptEngine.generate_timed_words(caption_text, 0.0, duration)
        return self.caption_engine.generate_ass_script(
            timed_words=timed_words,
            output_path=output_ass_path,
            words_per_line=words_per_line,
        )

    def prepare_dubbing_package(
        self,
        clip_id: str,
        category: str = "gaming",
        title: str = "",
        duration: float = 30.0,
        output_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Complete packaging: creates Hindi voiceover audio, ASS subtitles, and localized metadata."""
        if not output_dir:
            output_dir = os.path.join(str(BASE_DIR), "storage", "clips")
        os.makedirs(output_dir, exist_ok=True)

        script_data = self.select_script(category=category, title=title)
        hindi_text = script_data["hindi"]
        hinglish_subtitles = script_data["hinglish"]
        localized_title = script_data["title"]

        dub_audio_path = os.path.join(output_dir, f"{clip_id}_hindi_dub.mp3")
        ass_sub_path = os.path.join(output_dir, f"{clip_id}.ass")

        # 1. Synthesize audio
        audio_ok = self.synthesize_hindi_audio(hindi_text, dub_audio_path)

        # 2. Generate animated ASS subtitles (using high-retention Hinglish for maximum viewer retention)
        self.generate_animated_subtitles(
            caption_text=hinglish_subtitles,
            output_ass_path=ass_sub_path,
            duration=duration,
        )

        return {
            "is_dubbed": True,
            "language": "hi",
            "dubbed_audio_path": dub_audio_path if audio_ok else None,
            "ass_subtitle_path": ass_sub_path,
            "hindi_script": hindi_text,
            "hinglish_captions": hinglish_subtitles,
            "localized_title": localized_title,
        }
