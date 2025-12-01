"""Gerenciador simplificado de sessões - mostra apenas geração final"""
import os
import json
import pickle
from datetime import datetime

class SessionManager:
    def __init__(self, sessions_dir="sessions"):
        """Gerencia sessões de treinamento"""
        self.sessions_dir = sessions_dir
        self.sessions_file = os.path.join(sessions_dir, "sessions_history.json")
        self.current_session_id = None
        self.current_session_data = None
        self.current_best_fitness = 0
        
        self._create_directory()
        self._load_sessions_history()
        
    def _create_directory(self):
        """Cria diretório de sessões"""
        if not os.path.exists(self.sessions_dir):
            os.makedirs(self.sessions_dir)
            
    def _load_sessions_history(self):
        """Carrega histórico de sessões"""
        if os.path.exists(self.sessions_file):
            with open(self.sessions_file, 'r') as f:
                self.sessions_history = json.load(f)
        else:
            self.sessions_history = {
                "sessions": {},
                "global_best": None
            }
            self._save_sessions_history()
            
    def _save_sessions_history(self):
        """Salva histórico"""
        with open(self.sessions_file, 'w') as f:
            json.dump(self.sessions_history, f, indent=2)
    
    def delete_session(self, session_id):
        """Deleta uma sessão"""
        if session_id not in self.sessions_history["sessions"]:
            print(f"⚠ Sessão não encontrada: {session_id}")
            return False
        
        # Deleta arquivo do modelo
        model_file = self.sessions_history["sessions"][session_id]["model_file"]
        model_path = os.path.join(self.sessions_dir, model_file)
        
        if os.path.exists(model_path):
            os.remove(model_path)
            print(f"✓ Arquivo deletado: {model_file}")
        
        # Remove do histórico
        del self.sessions_history["sessions"][session_id]
        
        # Atualiza melhor global se necessário
        if (self.sessions_history["global_best"] and 
            self.sessions_history["global_best"]["session_id"] == session_id):
            
            # Procura novo melhor
            if self.sessions_history["sessions"]:
                best_session = max(self.sessions_history["sessions"].items(),
                                  key=lambda x: x[1]["best_fitness"])
                
                self.sessions_history["global_best"] = {
                    "session_id": best_session[0],
                    "fitness": best_session[1]["best_fitness"],
                    "generation": best_session[1]["best_generation"],
                    "model_file": best_session[1]["model_file"]
                }
            else:
                self.sessions_history["global_best"] = None
        
        self._save_sessions_history()
        print(f"✓ Sessão deletada: {session_id}")
        return True
            
    def start_new_session(self, start_generation=1):
        """Inicia nova sessão"""
        self.current_session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_session_data = {
            "session_id": self.current_session_id,
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": None,
            "start_generation": start_generation,
            "end_generation": start_generation,
            "best_fitness": 0,
            "best_generation": start_generation,
            "avg_fitness": 0,
            "model_file": f"{self.current_session_id}_best.pkl",
            "total_generations": 0
        }
        self.current_best_fitness = 0
        
        if start_generation > 1:
            print(f"\n📝 Nova sessão: {self.current_session_id}")
            print(f"   Continuando da geração: {start_generation}")
        else:
            print(f"\n📝 Nova sessão: {self.current_session_id}")
            print(f"   Iniciando do zero")
        
        return self.current_session_id
        
    def update_session(self, generation, best_fitness, avg_fitness, best_agent_brain):
        """Atualiza sessão"""
        if not self.current_session_data:
            raise ValueError("Nenhuma sessão ativa!")
        
        # Atualiza com a geração REAL (não relativa)
        self.current_session_data["end_generation"] = generation
        
        # Total de gerações treinadas NESTA sessão
        generations_trained = generation - self.current_session_data["start_generation"] + 1
        self.current_session_data["total_generations"] = generations_trained
        
        self.current_session_data["avg_fitness"] = avg_fitness
        
        if best_fitness > self.current_best_fitness:
            self.current_best_fitness = best_fitness
            self.current_session_data["best_fitness"] = best_fitness
            self.current_session_data["best_generation"] = generation
            self._save_session_best_model(best_agent_brain, best_fitness, generation)
            
    def end_session(self, best_agent_brain=None):
        """Finaliza sessão"""
        if not self.current_session_data:
            print("⚠ Nenhuma sessão ativa.")
            return
        
        self.current_session_data["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if best_agent_brain:
            self._save_session_best_model(
                best_agent_brain,
                self.current_session_data["best_fitness"],
                self.current_session_data["best_generation"]
            )
        
        self.sessions_history["sessions"][self.current_session_id] = self.current_session_data
        
        current_best = self.current_session_data["best_fitness"]
        
        if (self.sessions_history["global_best"] is None or 
            current_best > self.sessions_history["global_best"]["fitness"]):
            
            self.sessions_history["global_best"] = {
                "session_id": self.current_session_id,
                "fitness": current_best,
                "generation": self.current_session_data["best_generation"],
                "model_file": self.current_session_data["model_file"]
            }
            
            print(f"\n🏆 NOVO RECORDE GLOBAL! Fitness: {current_best:.0f}")
        
        self._save_sessions_history()
        
        final_gen = self.current_session_data["end_generation"]
        trained = self.current_session_data["total_generations"]
        
        print(f"\n✓ Sessão salva: {self.current_session_id}")
        print(f"  Geração final: {final_gen} (treinou {trained} gerações nesta sessão)")
        print(f"  Melhor fitness: {self.current_session_data['best_fitness']:.0f}")
        
        self.current_session_data = None
        self.current_session_id = None
        
    def _save_session_best_model(self, brain, fitness, generation):
        """Salva modelo"""
        model_path = os.path.join(self.sessions_dir, self.current_session_data["model_file"])
        
        model_data = {
            "session_id": self.current_session_id,
            "input_size": brain.input_size,
            "hidden_size": brain.hidden_size,
            "output_size": brain.output_size,
            "weights": brain.get_weights(),
            "fitness": fitness,
            "generation": generation,  # Geração REAL
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
            
    def load_session_model(self, session_id):
        """Carrega modelo de uma sessão"""
        if session_id not in self.sessions_history["sessions"]:
            raise ValueError(f"Sessão não encontrada: {session_id}")
        
        model_file = self.sessions_history["sessions"][session_id]["model_file"]
        model_path = os.path.join(self.sessions_dir, model_file)
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modelo não encontrado: {model_path}")
        
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        print(f"\n✓ Modelo carregado: {session_id}")
        print(f"  Fitness: {model_data['fitness']:.0f}")
        print(f"  Geração: {model_data['generation']}")
        
        return model_data
        
    def load_global_best_model(self):
        """Carrega o melhor modelo global"""
        if not self.sessions_history["global_best"]:
            raise ValueError("Nenhum modelo treinado!")
        
        best_session_id = self.sessions_history["global_best"]["session_id"]
        print(f"\n🏆 Carregando MELHOR modelo global...")
        
        return self.load_session_model(best_session_id)
        
    def list_all_sessions(self):
        """Lista todas as sessões"""
        if not self.sessions_history["sessions"]:
            return []
        
        sessions = []
        for session_id, data in self.sessions_history["sessions"].items():
            sessions.append({
                "id": session_id,
                "best_fitness": data["best_fitness"],
                "final_generation": data["end_generation"],  # Geração final
                "start_time": data["start_time"]
            })
        
        sessions.sort(key=lambda x: x["best_fitness"], reverse=True)
        return sessions
        
    def print_sessions_summary(self):
        """Imprime resumo de sessões"""
        print("\n" + "="*70)
        print("📊 HISTÓRICO DE SESSÕES")
        print("="*70)
        
        sessions = self.list_all_sessions()
        
        if not sessions:
            print("\n📭 Nenhuma sessão encontrada.")
            return
        
        if self.sessions_history["global_best"]:
            best = self.sessions_history["global_best"]
            print(f"\n🏆 MELHOR GLOBAL:")
            print(f"   Fitness: {best['fitness']:.0f}")
            print(f"   Geração: {best['generation']}")
            print(f"   Sessão: {best['session_id']}")
        
        print(f"\n📋 TODAS AS SESSÕES ({len(sessions)}):")
        print("-"*70)
        
        for i, session in enumerate(sessions, 1):
            marker = "🏆" if (self.sessions_history["global_best"] and 
                           session['id'] == self.sessions_history["global_best"]['session_id']) else "  "
            
            print(f"{marker} {i}. {session['id']}")
            print(f"      Fitness: {session['best_fitness']:.0f} | "
                  f"Geração: {session['final_generation']} | "
                  f"Data: {session['start_time']}")
