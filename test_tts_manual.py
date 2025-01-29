from src.utils.tts_engines import MultiTTS
import time

def test_tts():
    print("Initializing Multi-TTS system...")
    tts = MultiTTS()
    
    # Test each engine
    test_message = "This is a test of the text to speech system."
    
    print("\nTesting Local TTS...")
    tts.set_engine('local')
    tts.speak(test_message)
    time.sleep(3)
    
    print("\nTesting Google TTS...")
    tts.set_engine('google')
    tts.speak(test_message)
    time.sleep(5)
    
    # Only test Azure if credentials are configured
    if tts.engines['azure'].subscription_key:
        print("\nTesting Azure TTS...")
        tts.set_engine('azure')
        tts.speak(test_message)
        time.sleep(5)
    
    # Only test Amazon if credentials are configured
    if tts.engines['amazon'].aws_access_key:
        print("\nTesting Amazon Polly...")
        tts.set_engine('amazon')
        tts.speak(test_message)
        time.sleep(5)
    
    print("\nTesting voice controls...")
    tts.set_engine('local')
    
    # Test stop functionality
    print("Testing stop functionality...")
    tts.speak("This is a long message that should be interrupted")
    time.sleep(1)
    tts.stop()
    
    # Test different rates
    print("\nTesting different speech rates...")
    for rate in [100, 150, 200]:
        if hasattr(tts.engines['local'], 'engine'):
            tts.engines['local'].engine.setProperty('rate', rate)
            tts.speak(f"Speaking at rate {rate}")
            time.sleep(3)
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_tts()
