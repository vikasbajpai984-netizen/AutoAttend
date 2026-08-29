from resemblyzer import VoiceEncoder , preprocess_wav
import numpy as np 
import io
import librosa
import streamlit as st 

@st.cache_resource
def load_voice_encoder():
    return VoiceEncoder()

def get_voice_embeddings(audio_bytes):
    try :
        encoder = load_voice_encoder()
        audio , sr = librosa.load(io.BytesIO(audio_bytes), sr = 16000)
        wav = preprocess_wav(audio)
        embedding = encoder.embed_utterance(wav)
        return embedding.tolist()
    except Exception as e:
        st.error(f"Voice recognition error{e}")
        return None

def identify_speaker (new_embedding, candidates_dict, threshold = 0.65):
    if new_embedding is None or not candidates_dict:
        return None, 0.0
    
    best_stu_id = None
    best_score = -1.0
    
    for stu_id , stored_embedding in candidates_dict.items():
        if stored_embedding:
            similarity = np.dot(new_embedding, stored_embedding)
            if similarity > best_score:
                best_score = similarity
                best_stu_id = stu_id
                
    if best_score >= threshold:
        return best_stu_id, best_score
    
    return None, best_score 

def process_bulk_audio(audio_bytes , candidate_dict , threshold = 0.65):
    try :
        encoder = load_voice_encoder()
        audio , sr = librosa.load(io.BytesIO(audio_bytes), sr = 16000)
        segments = librosa.effects.split(audio, top_db=30)
        
        identified_results ={}
        
        for start , end in segments:
            if (end-start) < sr*0.5:
                continue
            segment_audio = audio[start:end]
            wav = preprocess_wav(segment_audio)
            embeddings = encoder.embed_utterance(wav)
            
            stu_id , score = identify_speaker(embeddings, candidate_dict, threshold)
            if stu_id :
                if stu_id not in identified_results or score > identified_results[stu_id]:
                    identified_results[stu_id] = score
                
        return identified_results
    except Exception as e :
        st.error(f"Bulk process error{e}")
        return {}
        
                
        
    