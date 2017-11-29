# -*- coding: utf-8 -*- 
import time
from ctypes import *
from io import BytesIO
import wave
import platform
import logging
import os

logging.basicConfig(level=logging.DEBUG)

BASEPATH=os.path.split(os.path.realpath(__file__))[0]

def play(filename):
    import pygame
    pygame.mixer.init(frequency=16000)
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue

def saveWave(raw_data,_tmpFile = 'test.wav'):
    f = wave.open(_tmpFile,'w')
    f.setparams((1, 2, 16000, 262720, 'NONE', 'not compressed'))
    f.writeframesraw(raw_data)
    f.close()
    return _tmpFile

def text_to_speech(src_text="�ⲻ������һ������",file_name = None):

    plat = platform.architecture()
    if plat[0] == '32bit':
        cur = cdll.LoadLibrary(BASEPATH + '/x86/libmsc.so')
    else:
        cur = cdll.LoadLibrary(BASEPATH + '/x64/libmsc.so')
       
	logging.error(BASEPATH)
    MSPLogin = cur.MSPLogin
    QTTSSessionBegin = cur.QTTSSessionBegin
    QTTSTextPut = cur.QTTSTextPut

    QTTSAudioGet = cur.QTTSAudioGet
    QTTSAudioGet.restype = c_void_p

    QTTSSessionEnd = cur.QTTSSessionEnd
    
    ret_c = c_int(0)
    ret = 0

    ret = MSPLogin(None,None,'appid = 5947be90, work_dir = .') 
    if ret != 0:
        logging.error("MSPLogin failed, error code: " + ret);
        return

    session_begin_params="engine_type = local,voice_name = xiaoyan, text_encoding = UTF8, tts_res_path = fo|res/tts/xiaoyan.jet;fo|res/tts/common.jet, sample_rate = 16000, speed = 50, volume = 50, pitch = 50, rdn = 2"
       #session_begin_params="voice_name = xiaoyan, text_encoding = utf8, sample_rate = 16000, speed = 50, volume = 50, pitch = 50, rdn = 2"
    sessionID = QTTSSessionBegin(session_begin_params, byref(ret_c));
    if ret_c.value != 0 :
        logging.error("QTTSSessionBegin failed, error code: " + ret_c.value);
        return

    ret = QTTSTextPut(sessionID, src_text, len(src_text),None)
    if ret != 0:
        logging.error("QTTSTextPut failed, error code: " + ret);
        QTTSSessionEnd(sessionID, "TextPutError");
        
        return
    logging.info("���ںϳ� [%s]..." %(src_text))

    audio_len = c_uint(0)
    synth_status = c_int(0)

    f = BytesIO()
    while True:
        p = QTTSAudioGet(sessionID, byref(audio_len), byref(synth_status), byref(ret_c));
        if ret_c.value != 0:
            logging.error("QTTSAudioGet failed, error code: " + ret_c.value);
            QTTSSessionEnd(sessionID, "AudioGetError");
            break

        if p != None:
            buf = (c_char * audio_len.value).from_address(p)
            f.write(buf)

        if synth_status.value == 2 :
            saveWave(f.getvalue(),file_name)
            break

        #logging.debug(".")
		
        logging.debug(f.getvalue())
        #time.sleep(1)

    logging.info('�ϳ���ɣ�')
    ret = QTTSSessionEnd(sessionID, "Normal");
    if ret != 0:
        logging.error("QTTSTextPut failed, error code: " + ret);


if __name__ == '__main__':
    text_to_speech('tset','xx.wav')