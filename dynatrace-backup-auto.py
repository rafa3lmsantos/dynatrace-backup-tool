#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Dynatrace Configuration Backup Tool
Backup automático das configurações do Dynatrace usando Monaco CLI

Author: GitHub Community
License: MIT
Version: 1.0.0
"""

import os
import sys
import platform
import subprocess
import urllib.request
import threading
import time
import re
from pathlib import Path
from datetime import datetime

# Tentativa de importar requests (opcional)
try:
    import requests  # type: ignore  # pylint: disable=import-error
    HAS_REQUESTS = True
except ImportError:
    # requests não está disponível, usaremos urllib como fallback
    HAS_REQUESTS = False

class DynatraceBackup:
    def __init__(self):
        # Carregar configurações
        self.base_url = self._get_cluster_url()
        self.token = self._get_token()
        
        if not self.base_url:
            print("❌ Erro: URL do cluster não configurada!")
            print("📋 Edite o arquivo .env e defina DT_CLUSTER_URL")
            sys.exit(1)
            
        if not self.token:
            print("❌ Erro: Token não configurado!")
            print("📋 Edite o arquivo .env e defina DT_API_TOKEN")
            sys.exit(1)
            
        self.system = platform.system().lower()
        self.arch = self._get_architecture()
        self.script_dir = Path(__file__).parent
        self.backup_dir = self.script_dir / "backups"
        self.monaco_path = self._get_monaco_path()
        
        # Estatísticas do backup
        self.stats = {
            'start_time': None,
            'end_time': None,
            'total_configs': 0,
            'successful_configs': 0,
            'failed_configs': 0,
            'warnings': 0,
            'errors': [],
            'warnings_list': [],
            'progress_data': []
        }
        
    def _get_cluster_url(self):
        """Obtém URL do cluster de variáveis de ambiente ou arquivo .env"""
        # 1. Variáveis de ambiente
        url = os.getenv("DT_CLUSTER_URL") or os.getenv("DYNATRACE_CLUSTER_URL")
        if url:
            return url
            
        # 2. Arquivo .env (no mesmo diretório do script)
        script_dir = Path(__file__).parent
        env_file = script_dir / ".env"
        if env_file.exists():
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("DT_CLUSTER_URL="):
                            return line.split("=", 1)[1].strip().strip('"\'')
            except Exception:
                pass
        
        return None
    
    def _get_token(self):
        """Obtém token de API de variáveis de ambiente ou arquivo .env"""
        # 1. Variáveis de ambiente
        token = (os.getenv("DT_API_TOKEN") or 
                os.getenv("DYNATRACE_API_TOKEN") or 
                os.getenv("DYNATRACE_TOKEN"))
        if token:
            return token
            
        # 2. Arquivo .env (no mesmo diretório do script)
        script_dir = Path(__file__).parent
        env_file = script_dir / ".env"
        if env_file.exists():
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("DT_API_TOKEN="):
                            return line.split("=", 1)[1].strip().strip('"\'')
            except Exception:
                pass
        
        return None
    
    def _get_architecture(self):
        """Detecta arquitetura do sistema"""
        arch = platform.machine().lower()
        if arch in ['x86_64', 'amd64']:
            return 'amd64'
        elif arch in ['arm64', 'aarch64']:
            return 'arm64'
        else:
            return 'amd64'  # Default
    
    def _get_monaco_path(self):
        """Determina caminho do Monaco CLI"""
        if self.system == 'windows':
            return self.script_dir / "monaco.exe"
        else:
            return self.script_dir / "monaco"
    
    def _mask_token(self, token):
        """Mascara token para logs"""
        if not token or len(token) < 10:
            return "***"
        return f"{token[:8]}...{token[-4:]}"
    
    def _get_python_version(self):
        """Obtém versão do Python"""
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    def print_header(self, title):
        """Imprime cabeçalho formatado"""
        print("=" * 70)
        print(f"🚀 {title}")
        print("=" * 70)
    
    def monitor_progress(self, process, backup_path):
        """Monitora progresso do backup em tempo real"""
        print("\n📊 MONITORAMENTO DO BACKUP:")
        print("=" * 50)
        
        last_count = 0
        start_time = time.time()
        
        while process.poll() is None:
            try:
                # Contar arquivos criados
                if backup_path.exists():
                    current_count = sum(1 for _ in backup_path.rglob('*') if _.is_file())
                    
                    if current_count > last_count:
                        elapsed = time.time() - start_time
                        rate = current_count / elapsed if elapsed > 0 else 0
                        
                        print(f"📁 Arquivos processados: {current_count:,} | "
                              f"⏱️ Tempo: {elapsed:.1f}s | "
                              f"🚀 Taxa: {rate:.1f} arq/s", end='\r')
                        
                        last_count = current_count
                
                time.sleep(2)  # Atualizar a cada 2 segundos
                
            except Exception:
                pass
        
        print("\n")  # Nova linha após o monitoramento
    
    def parse_monaco_output(self, output):
        """Analisa saída do Monaco para estatísticas"""
        if not output:
            return
        
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Contar warnings
            if 'level=WARN' in line:
                self.stats['warnings'] += 1
                # Extrair mensagem do warning
                warn_match = re.search(r'msg="([^"]+)"', line)
                if warn_match:
                    self.stats['warnings_list'].append(warn_match.group(1))
            
            # Contar erros
            elif 'level=ERROR' in line:
                self.stats['failed_configs'] += 1
                # Extrair mensagem do erro
                error_match = re.search(r'msg="([^"]+)"', line)
                if error_match:
                    self.stats['errors'].append(error_match.group(1))
            
            # Detectar progresso
            elif 'Downloading' in line or 'Downloaded' in line:
                self.stats['progress_data'].append({
                    'timestamp': datetime.now(),
                    'message': line
                })
    
    def print_statistics(self, backup_path, duration):
        """Imprime estatísticas detalhadas do backup"""
        print("\n" + "="*70)
        print("📊 ESTATÍSTICAS DO BACKUP")
        print("="*70)
        
        # Contar arquivos por tipo
        file_counts = {}
        total_size = 0
        
        for file_path in backup_path.rglob('*'):
            if file_path.is_file():
                ext = file_path.suffix.lower() or 'sem_extensão'
                file_counts[ext] = file_counts.get(ext, 0) + 1
                try:
                    total_size += file_path.stat().st_size
                except:
                    pass
        
        total_files = sum(file_counts.values())
        
        print(f"📁 Total de arquivos: {total_files:,}")
        print(f"💾 Tamanho total: {self._format_size(total_size)}")
        print(f"⏱️ Duração: {duration:.1f} segundos")
        print(f"🚀 Taxa média: {total_files/duration:.1f} arquivos/segundo")
        
        print(f"\n✅ Configurações bem-sucedidas: {self.stats['successful_configs']}")
        print(f"❌ Configurações com erro: {self.stats['failed_configs']}")
        print(f"⚠️ Avisos encontrados: {self.stats['warnings']}")
        
        # Top 5 tipos de arquivo
        if file_counts:
            print(f"\n📋 Tipos de arquivo mais comuns:")
            sorted_types = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)
            for ext, count in sorted_types[:5]:
                percentage = (count / total_files) * 100
                print(f"   {ext}: {count:,} arquivos ({percentage:.1f}%)")
        
        # Mostrar alguns erros se houver
        if self.stats['errors']:
            print(f"\n❌ Primeiros erros encontrados:")
            for i, error in enumerate(self.stats['errors'][:3]):
                print(f"   {i+1}. {error[:80]}...")
        
        # Mostrar alguns warnings se houver
        if self.stats['warnings_list']:
            print(f"\n⚠️ Principais avisos:")
            unique_warnings = list(set(self.stats['warnings_list']))
            for i, warning in enumerate(unique_warnings[:3]):
                print(f"   {i+1}. {warning[:80]}...")
    
    def _format_size(self, size_bytes):
        """Formata tamanho em bytes para formato legível"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def validate_environment(self):
        """Valida ambiente e dependências"""
        print("ℹ️ Validando ambiente...")
        
        # Python
        print("ℹ️ Verificando instalação do Python...")
        python_version = self._get_python_version()
        print(f"✅ Python {python_version} encontrado - OK!")
        
        # Requests (opcional)
        print("ℹ️ Verificando dependências Python...")
        if HAS_REQUESTS:
            print("✅ ✓ requests disponível")
        else:
            print("ℹ️ ○ requests não disponível (usando urllib)")
        
        # Token
        print(f"✅ Token encontrado: {self._mask_token(self.token)}")
        
        # Sistema
        print(f"✅ Sistema: {platform.system()} {platform.release()}")
        print(f"✅ Python: {python_version}")
        
        return True
    
    def check_monaco(self):
        """Verifica Monaco CLI"""
        print("ℹ️ Verificando Monaco CLI...")
        
        if not self.monaco_path.exists():
            print("⚠️ Monaco não encontrado, baixando...")
            if not self.download_monaco():
                print("❌ Falha ao baixar Monaco CLI")
                return False
        
        # Testar Monaco
        try:
            result = subprocess.run([str(self.monaco_path), "version"], 
                                 capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ Monaco encontrado: {self.monaco_path}")
                return True
        except Exception:
            pass
        
        print("❌ Monaco CLI não está funcionando")
        return False
    
    def download_monaco(self):
        """Baixa Monaco CLI"""
        print("🔄 Baixando Monaco CLI...")
        
        # URLs para diferentes plataformas
        urls = {
            'windows': f"https://github.com/dynatrace/dynatrace-configuration-as-code/releases/latest/download/monaco-windows-{self.arch}.exe",
            'linux': f"https://github.com/dynatrace/dynatrace-configuration-as-code/releases/latest/download/monaco-linux-{self.arch}",
            'darwin': f"https://github.com/dynatrace/dynatrace-configuration-as-code/releases/latest/download/monaco-darwin-{self.arch}"
        }
        
        url = urls.get(self.system)
        if not url:
            print(f"❌ Sistema não suportado: {self.system}")
            return False
        
        try:
            if HAS_REQUESTS:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                self.monaco_path.write_bytes(response.content)
            else:
                urllib.request.urlretrieve(url, self.monaco_path)
            
            # Dar permissão de execução (Unix)
            if self.system != 'windows':
                os.chmod(self.monaco_path, 0o755)
            
            print(f"✅ Monaco baixado: {self.monaco_path}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao baixar Monaco: {e}")
            return False
    
    def test_connectivity(self):
        """Testa conectividade com Dynatrace"""
        print("🔄 Testando conectividade...")
        
        test_url = f"{self.base_url}/api/v1/config/clusterversion"
        headers = {"Authorization": f"Api-Token {self.token}"}
        
        try:
            if HAS_REQUESTS:
                response = requests.get(test_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    print("✅ Conectividade OK!")
                    return True
                else:
                    print(f"⚠️ Resposta inesperada: {response.status_code}")
            else:
                req = urllib.request.Request(test_url)
                req.add_header("Authorization", f"Api-Token {self.token}")
                with urllib.request.urlopen(req, timeout=10) as response:
                    if response.status == 200:
                        print("✅ Conectividade OK!")
                        return True
        except Exception as e:
            print(f"⚠️ Aviso: Teste de conectividade inconclusivo, mas continuando...")
        
        return True  # Continua mesmo com teste inconclusivo
    
    def create_monaco_config(self):
        """Cria configuração do Monaco"""
        print("🔄 Criando configuração Monaco...")
        
        config_dir = self.script_dir / "monaco-config"
        config_dir.mkdir(exist_ok=True)
        
        # Arquivo environments.yaml
        env_config = f"""environments:
  {self.base_url}:
    - name: "production"
      - url:
        value: "{self.base_url}"
      - token:
        value: "{self.token}"
"""
        
        env_file = config_dir / "environments.yaml"
        env_file.write_text(env_config, encoding='utf-8')
        
        print(f"✅ Configuração criada: {env_file}")
        return str(config_dir)
    
    def run_backup(self):
        """Executa backup das configurações"""
        print("🔄 Executando backup...")
        
        # Inicializar estatísticas
        self.stats['start_time'] = datetime.now()
        
        # Criar diretório de backup com formato brasileiro (dia_mes_ano_hora_minuto_segundo)
        timestamp = datetime.now().strftime("%d_%m_%Y_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(parents=True, exist_ok=True)
        
        print(f"ℹ️ Salvando em: {backup_path}")
        print("🔄 Iniciando backup... (monitoramento em tempo real)")
        
        # Definir variável de ambiente temporária para o token
        env = os.environ.copy()
        env["DT_TOKEN"] = self.token
        
        # Comando Monaco
        cmd = [
            str(self.monaco_path),
            "download",
            "--url", self.base_url,
            "--token", "DT_TOKEN",
            "--output-folder", str(backup_path),
            "--project", "project"
        ]
        
        try:
            # Executar Monaco com monitoramento
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,
                text=True,
                cwd=str(self.script_dir), 
                env=env,
                universal_newlines=True
            )
            
            # Iniciar monitoramento em thread separada
            monitor_thread = threading.Thread(
                target=self.monitor_progress, 
                args=(process, backup_path)
            )
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # Capturar saída linha por linha
            output_lines = []
            while True:
                line = process.stdout.readline()
                if line == '' and process.poll() is not None:
                    break
                if line:
                    output_lines.append(line.strip())
            
            # Aguardar processo terminar
            return_code = process.wait()
            
            # Finalizar estatísticas
            self.stats['end_time'] = datetime.now()
            duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
            
            # Analisar saída
            full_output = '\n'.join(output_lines)
            self.parse_monaco_output(full_output)
            
            if return_code == 0:
                # Contar arquivos salvos
                file_count = sum(1 for _ in backup_path.rglob('*') if _.is_file())
                self.stats['successful_configs'] = file_count
                
                print(f"\n✅ Backup concluído com sucesso!")
                print(f"📁 Local: {backup_path}")
                
                # Mostrar estatísticas detalhadas
                self.print_statistics(backup_path, duration)
                
                return True
            else:
                print(f"\n❌ Erro no backup (código: {return_code})")
                
                # Analisar erros mesmo em caso de falha
                self.print_statistics(backup_path, duration)
                
                if full_output:
                    print(f"\nDetalhes do erro:")
                    # Mostrar últimas linhas do output
                    error_lines = full_output.split('\n')[-10:]
                    for line in error_lines:
                        if line.strip():
                            print(f"   {line}")
                
                return False
                
        except Exception as e:
            print(f"\n❌ Erro ao executar backup: {e}")
            return False
    
    def run(self):
        """Executa processo completo de backup"""
        self.print_header("DYNATRACE BACKUP")
        
        try:
            # Validações
            if not self.validate_environment():
                return False
            
            if not self.check_monaco():
                return False
            
            if not self.test_connectivity():
                return False
            
            # Backup
            if not self.run_backup():
                return False
            
            # Sucesso
            self.print_header("BACKUP CONCLUÍDO COM SUCESSO!")
            print("🎉 Todas as configurações foram salvas!")
            print(f"📁 Verifique a pasta: {self.backup_dir}")
            print("=" * 70)
            
            return True
            
        except KeyboardInterrupt:
            print("\n\n❌ Operação cancelada pelo usuário.")
            return False
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
            return False

def main():
    """Função principal"""
    backup = DynatraceBackup()
    success = backup.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
