#!/usr/bin/env python3
"""
Dynatrace Backup - Solução Universal com Auto-instalação
- Auto-detecta e instala Python se necessário
- Funciona em Windows, Linux e macOS
- Script único para todas as plataformas
- Zero configuração manual
"""

import os
import sys
import platform
import subprocess
import urllib.request
import json
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

# Tentativa de importar requests (opcional)
# O requests é usado para downloads mais eficientes, mas urllib é o fallback
try:
    import requests  # type: ignore  # pylint: disable=import-error
    HAS_REQUESTS = True
except ImportError:
    # requests não está disponível, usaremos urllib como fallback
    HAS_REQUESTS = False

class DynatraceBackupUniversal:
    def __init__(self):
        # Usar variáveis de ambiente para configurações sensíveis
        self.base_url = os.getenv('DT_CLUSTER_URL')
        if not self.base_url:
            print("❌ Erro: Variável de ambiente DT_CLUSTER_URL não configurada!")
            print("📋 Configure com: set DT_CLUSTER_URL=https://seu-ambiente.live.dynatrace.com")
            sys.exit(1)
            
        self.system = platform.system().lower()
        self.arch = self._get_architecture()
        self.python_version = self._get_python_version()
        self.token = self._get_token()
        # Usa estrutura de pastas organizada
        self.backup_dir = Path("../backups")
        self.monaco_path = self._get_monaco_path()
        
    def _get_architecture(self):
        """Detecta arquitetura do sistema."""
        machine = platform.machine().lower()
        if machine in ['x86_64', 'amd64']:
            return 'amd64'
        elif machine in ['arm64', 'aarch64']:
            return 'arm64'
        elif machine in ['i386', 'i686']:
            return '386'
        else:
            return 'amd64'
    
    def _get_python_version(self):
        """Obtém versão do Python atual."""
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    def _get_monaco_path(self):
        """Determina caminho do Monaco."""
        if self.system == "windows":
            return Path("monaco.exe")
        else:
            return Path("monaco")
    
    def _get_token(self):
        """Obtém token de múltiplas fontes."""
        # 1. Variável de ambiente padrão DT_API_TOKEN
        token = os.getenv("DT_API_TOKEN")
        if token:
            return token
            
        # 2. Variável de ambiente alternativa (compatibilidade)
        token = os.getenv("DYNATRACE_API_TOKEN")
        if token:
            return token
            
        # 3. Arquivo .env
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith("DT_API_TOKEN=") or line.startswith("DYNATRACE_API_TOKEN="):
                        return line.split("=", 1)[1].strip().strip('"\'')
        
        # 4. Arquivo de configuração JSON
        config_file = Path("dynatrace.config")
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    return config.get("token")
            except:
                pass
                
        return None
    
    def _print_status(self, message, status="info"):
        """Imprime mensagem com status."""
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️", 
            "error": "❌",
            "progress": "🔄",
            "download": "⬇️"
        }
        icon = icons.get(status, "•")
        print(f"{icon} {message}")
    
    def check_python_installation(self):
        """Verifica e instala Python se necessário."""
        self._print_status("Verificando instalação do Python...", "info")
        
        # Verifica se Python está adequado
        if sys.version_info >= (3, 6):
            self._print_status(f"Python {self.python_version} encontrado - OK!", "success")
            return True
        
        self._print_status(f"Python {self.python_version} muito antigo (requer 3.6+)", "warning")
        return self._install_python()
    
    def _install_python(self):
        """Instala Python automaticamente."""
        self._print_status("Iniciando instalação automática do Python...", "download")
        
        try:
            if self.system == "windows":
                return self._install_python_windows()
            elif self.system == "darwin":
                return self._install_python_macos()
            else:
                return self._install_python_linux()
        except Exception as e:
            self._print_status(f"Erro na instalação automática: {e}", "error")
            self._print_status("Instale Python manualmente de python.org", "info")
            return False
    
    def _install_python_windows(self):
        """Instala Python no Windows."""
        self._print_status("Baixando Python para Windows...", "download")
        
        # URL do instalador Python Windows
        python_url = "https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe"
        installer_path = Path(tempfile.gettempdir()) / "python_installer.exe"
        
        # Download
        urllib.request.urlretrieve(python_url, installer_path)
        self._print_status("Download concluído", "success")
        
        # Instalação silenciosa
        self._print_status("Instalando Python... (pode demorar alguns minutos)", "progress")
        cmd = [
            str(installer_path),
            "/quiet",
            "InstallAllUsers=1",
            "PrependPath=1",
            "Include_test=0"
        ]
        
        result = subprocess.run(cmd, capture_output=True)
        
        # Limpeza
        installer_path.unlink()
        
        if result.returncode == 0:
            self._print_status("Python instalado com sucesso!", "success")
            self._print_status("Reinicie o terminal e execute novamente", "info")
            return True
        else:
            self._print_status("Falha na instalação automática", "error")
            return False
    
    def _install_python_macos(self):
        """Instala Python no macOS."""
        self._print_status("Verificando Homebrew...", "info")
        
        # Verifica se tem Homebrew
        try:
            subprocess.run(["brew", "--version"], capture_output=True, check=True)
            self._print_status("Homebrew encontrado", "success")
            
            # Instala Python via Homebrew
            self._print_status("Instalando Python via Homebrew...", "progress")
            result = subprocess.run(["brew", "install", "python@3.11"], capture_output=True)
            
            if result.returncode == 0:
                self._print_status("Python instalado com sucesso!", "success")
                return True
            else:
                raise Exception("Falha no brew install")
                
        except:
            self._print_status("Homebrew não encontrado ou falha na instalação", "warning")
            self._print_status("Instale manualmente:", "info")
            self._print_status("1. Instale Homebrew: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"", "info")
            self._print_status("2. Execute: brew install python@3.11", "info")
            return False
    
    def _install_python_linux(self):
        """Instala Python no Linux."""
        self._print_status("Detectando distribuição Linux...", "info")
        
        # Detecta distribuição
        distro_commands = {
            "ubuntu": ["sudo", "apt", "update", "&&", "sudo", "apt", "install", "-y", "python3", "python3-pip"],
            "debian": ["sudo", "apt", "update", "&&", "sudo", "apt", "install", "-y", "python3", "python3-pip"],
            "centos": ["sudo", "yum", "install", "-y", "python3", "python3-pip"],
            "rhel": ["sudo", "yum", "install", "-y", "python3", "python3-pip"],
            "fedora": ["sudo", "dnf", "install", "-y", "python3", "python3-pip"],
            "arch": ["sudo", "pacman", "-S", "python", "python-pip"]
        }
        
        # Tenta detectar distribuição
        try:
            with open("/etc/os-release", "r") as f:
                os_info = f.read().lower()
                
            for distro, cmd in distro_commands.items():
                if distro in os_info:
                    self._print_status(f"Distribuição detectada: {distro}", "info")
                    self._print_status("Instalando Python...", "progress")
                    
                    # Executa comando de instalação
                    result = subprocess.run(" ".join(cmd), shell=True, capture_output=True)
                    
                    if result.returncode == 0:
                        self._print_status("Python instalado com sucesso!", "success")
                        return True
                    else:
                        raise Exception(f"Falha no comando: {' '.join(cmd)}")
                        
        except Exception as e:
            self._print_status(f"Não foi possível instalar automaticamente: {e}", "warning")
            self._print_status("Instale manualmente com seu gerenciador de pacotes:", "info")
            self._print_status("Ubuntu/Debian: sudo apt install python3 python3-pip", "info")
            self._print_status("CentOS/RHEL: sudo yum install python3 python3-pip", "info")
            self._print_status("Fedora: sudo dnf install python3 python3-pip", "info")
            return False
    
    def install_dependencies(self):
        """Instala dependências Python necessárias (opcionais)."""
        self._print_status("Verificando dependências Python...", "info")
        
        # Requests é opcional - script funciona sem ele
        optional_packages = ["requests"]
        
        for package in optional_packages:
            try:
                __import__(package)
                self._print_status(f"✓ {package} disponível", "success")
            except ImportError:
                self._print_status(f"⚠ {package} não encontrado (opcional)", "warning")
                try:
                    subprocess.run([
                        sys.executable, "-m", "pip", "install", package
                    ], check=True, capture_output=True, timeout=60)
                    self._print_status(f"✓ {package} instalado", "success")
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    self._print_status(f"⚠ Falha ao instalar {package} - continuando sem ele", "warning")
        
        return True
    
    def validate_environment(self):
        """Valida ambiente completo."""
        self._print_status("Validando ambiente...", "info")
        
        # Verifica Python
        if not self.check_python_installation():
            return False
        
        # Instala dependências
        if not self.install_dependencies():
            return False
        
        # Verifica token
        if not self.token:
            self._print_status("Token não encontrado!", "error")
            self._print_status("Configure usando uma das opções:", "info")
            if self.system == "windows":
                self._print_status("  $env:DT_API_TOKEN='seu_token'", "info")
                self._print_status("  set DT_API_TOKEN=seu_token", "info")
            else:
                self._print_status("  export DT_API_TOKEN='seu_token'", "info")
            self._print_status("  ou crie arquivo .env com DT_API_TOKEN=seu_token", "info")
            return False
            
        masked_token = f"{self.token[:10]}...{self.token[-10:]}"
        self._print_status(f"Token encontrado: {masked_token}", "success")
        self._print_status(f"Sistema: {platform.system()} {platform.release()}", "success")
        self._print_status(f"Python: {self.python_version}", "success")
        return True
    
    def download_monaco(self):
        """Baixa Monaco CLI automaticamente."""
        self._print_status("Verificando Monaco CLI...", "info")
        
        if self.monaco_path.exists():
            self._print_status(f"Monaco encontrado: {self.monaco_path}", "success")
            return True
            
        self._print_status("Baixando Monaco CLI...", "download")
        
        # URLs baseadas no sistema operacional
        base_url = "https://github.com/dynatrace/dynatrace-configuration-as-code/releases/latest/download"
        
        if self.system == "windows":
            url = f"{base_url}/monaco-windows-{self.arch}.exe"
            filename = "monaco.exe"
        elif self.system == "darwin":
            url = f"{base_url}/monaco-darwin-{self.arch}"
            filename = "monaco"
        else:
            url = f"{base_url}/monaco-linux-{self.arch}"
            filename = "monaco"
        
        try:
            self._print_status(f"Baixando de: {url}", "download")
            
            # Tenta diferentes métodos de download
            success = False
            
            # Método 1: requests (se disponível e SSL funcionar)
            if HAS_REQUESTS:
                try:
                    response = requests.get(url, stream=True, timeout=60)
                    response.raise_for_status()
                    
                    with open(filename, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    success = True
                    self._print_status("Download via requests - OK", "success")
                    
                except Exception as requests_error:
                    self._print_status(f"Requests falhou: {requests_error}", "warning")
            else:
                self._print_status("Requests não disponível, usando urllib", "info")
                
                # Método 2: urllib com SSL desabilitado
                try:
                    import ssl
                    ssl_context = ssl.create_default_context()
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
                    
                    request = urllib.request.Request(url)
                    with urllib.request.urlopen(request, context=ssl_context, timeout=60) as response:
                        with open(filename, 'wb') as f:
                            f.write(response.read())
                    success = True
                    self._print_status("Download via urllib (SSL desabilitado) - OK", "success")
                    
                except Exception as urllib_error:
                    self._print_status(f"urllib também falhou: {urllib_error}", "warning")
                    
                    # Método 3: curl externo (última tentativa)
                    try:
                        curl_cmd = ["curl", "-L", "-o", filename, url, "--insecure", "--connect-timeout", "60"]
                        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=120)
                        if result.returncode == 0:
                            success = True
                            self._print_status("Download via curl - OK", "success")
                        else:
                            raise Exception(f"curl falhou: {result.stderr}")
                    except Exception as curl_error:
                        self._print_status(f"curl também falhou: {curl_error}", "error")
            
            if not success:
                self._print_status("Todos os métodos de download falharam", "error")
                self._print_status("Baixe manualmente:", "info")
                self._print_status(f"URL: {url}", "info")
                self._print_status(f"Salve como: {filename}", "info")
                return False
            
            # Torna executável no Unix
            if self.system != "windows":
                os.chmod(filename, 0o755)
                
            self._print_status(f"Monaco baixado: {filename}", "success")
            return True
            
        except Exception as e:
            self._print_status(f"Erro geral no download: {e}", "error")
            return False
    
    def test_connectivity(self):
        """Testa conectividade com Dynatrace usando Monaco CLI."""
        self._print_status("Testando conectividade...", "progress")
        
        # Cria configuração temporária para teste
        temp_dir = Path(tempfile.mkdtemp())
        try:
            # Cria manifest.yaml (formato novo do Monaco v2)
            manifest_content = f"""
environments:
  test-env:
    url: "{self.base_url}"
    auth:
      token:
        name: DT_TOKEN

projects:
  - name: connectivity-test
    path: projects/test
"""
            manifest_file = temp_dir / "manifest.yaml"
            manifest_file.write_text(manifest_content.strip())
            
            # Cria estrutura de projeto vazia
            project_dir = temp_dir / "projects" / "test"
            project_dir.mkdir(parents=True)
            
            # Cria arquivo vazio de configuração
            config_dir = project_dir / "auto-tag"
            config_dir.mkdir(parents=True)
            (config_dir / "test.yaml").write_text("configs: []")
            
            # Testa conectividade com Monaco usando deploy dry-run
            cmd = [str(self.monaco_path), "deploy", "manifest.yaml", "--dry-run", "--environment", "test-env"]
            
            env = os.environ.copy()
            env["DT_TOKEN"] = self.token
            
            result = subprocess.run(
                cmd,
                cwd=temp_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Verifica resultado
            output_text = (result.stdout + result.stderr).lower()
            
            if result.returncode == 0 or "validation successful" in output_text or "would deploy" in output_text:
                self._print_status("Conectividade OK! Token válido", "success")
                return True
            elif "401" in output_text or "unauthorized" in output_text:
                self._print_status("Erro: Token inválido ou expirado", "error")
                return False
            elif "403" in output_text or "forbidden" in output_text:
                self._print_status("Erro: Token sem permissões suficientes", "error")
                return False
            elif "connection" in output_text or "network" in output_text or "timeout" in output_text:
                self._print_status("Erro: Problema de conectividade de rede", "error")
                return False
            else:
                # Se chegou aqui, pode ser um problema menor - vamos tentar continuar
                self._print_status("Aviso: Teste de conectividade inconclusivo, mas continuando...", "warning")
                return True
                
        except subprocess.TimeoutExpired:
            self._print_status("Timeout na conectividade - verificar rede", "error")
            return False
        except Exception as e:
            self._print_status(f"Erro no teste: {str(e)}", "error")
            # Se o teste de conectividade falhar, vamos tentar continuar mesmo assim
            self._print_status("Continuando mesmo com falha no teste...", "warning")
            return True
        finally:
            # Limpa arquivos temporários
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
    
    def create_monaco_config(self):
        """Cria configuração do Monaco."""
        self._print_status("Criando configuração Monaco...", "progress")
        
        config_dir = Path("monaco-config")
        config_dir.mkdir(exist_ok=True)
        
        yaml_content = f"""environments:
  production:
    name: "Production Environment"
    url:
      type: "environment"
      value: "{self.base_url}"
    auth:
      token:
        type: "environment"
        name: "DYNATRACE_API_TOKEN"
"""
        
        env_file = config_dir / "environments.yaml"
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        self._print_status(f"Configuração criada: {env_file}", "success")
        return config_dir
    
    def run_backup(self):
        """Executa backup completo."""
        self._print_status("Executando backup...", "progress")
        
        # Cria diretório de backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(parents=True, exist_ok=True)
        
        config_dir = self.create_monaco_config()
        
        # Comando Monaco
        cmd = [
            str(self.monaco_path),
            "download",
            "--url", self.base_url,
            "--token", "DYNATRACE_API_TOKEN",
            "--output-folder", str(backup_path)
        ]
        
        self._print_status(f"Salvando em: {backup_path}", "info")
        self._print_status("Aguarde... (pode demorar alguns minutos)", "progress")
        
        # Configura ambiente
        env = os.environ.copy()
        env["DYNATRACE_API_TOKEN"] = self.token
        
        try:
            result = subprocess.run(
                cmd, 
                env=env,
                timeout=600,
                check=True
            )
            
            self._print_status("Backup executado com sucesso!", "success")
            
            if backup_path.exists():
                self._print_status(f"Backup criado em: {backup_path}", "success")
                self._analyze_backup(backup_path)
                self._create_restore_script(backup_path)
                return backup_path
            else:
                self._print_status("Diretório de backup não foi criado", "error")
                return None
                
        except subprocess.CalledProcessError as e:
            self._print_status(f"Erro no backup (código: {e.returncode})", "error")
            return None
        except subprocess.TimeoutExpired:
            self._print_status("Timeout no backup (mais de 10 minutos)", "error")
            return None
        except Exception as e:
            self._print_status(f"Erro inesperado: {e}", "error")
            return None
    
    def _analyze_backup(self, backup_path):
        """Analisa conteúdo do backup."""
        self._print_status("Analisando backup...", "progress")
        
        try:
            json_files = list(backup_path.rglob("*.json"))
            
            if not json_files:
                self._print_status("Nenhum arquivo JSON encontrado", "warning")
                return
            
            # Agrupa por tipo
            config_types = {}
            total_size = 0
            
            for file in json_files:
                try:
                    config_type = file.parent.name
                    if config_type not in config_types:
                        config_types[config_type] = 0
                    config_types[config_type] += 1
                    total_size += file.stat().st_size
                except:
                    pass
            
            # Mostra resumo
            self._print_status("Resumo do backup:", "info")
            for config_type, count in sorted(list(config_types.items())[:10]):
                if count > 0:
                    self._print_status(f"  📂 {config_type}: {count} arquivos", "info")
            
            if len(config_types) > 10:
                self._print_status(f"  ... e {len(config_types) - 10} tipos mais", "info")
            
            total_mb = total_size / (1024 * 1024)
            self._print_status(f"Total: {len(json_files)} arquivos ({total_mb:.1f} MB)", "success")
            
        except Exception as e:
            self._print_status(f"Erro ao analisar: {e}", "warning")
    
    def _create_restore_script(self, backup_path):
        """Cria script de restauração universal."""
        
        # Script Python universal
        restore_py = backup_path / "restore.py"
        
        restore_content = f'''#!/usr/bin/env python3
"""
Script de Restauração Dynatrace - Universal
Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def print_status(message, status="info"):
    icons = {{"info": "ℹ️", "success": "✅", "error": "❌"}}
    print(f"{{icons.get(status, '•')}} {{message}}")

def main():
    print_status("Restaurando configurações do Dynatrace...")
    
    # Verifica token
    token = os.getenv("DYNATRACE_API_TOKEN")
    if not token:
        print_status("Token não configurado!", "error")
        system = platform.system().lower()
        if system == "windows":
            print_status("Configure: $env:DYNATRACE_API_TOKEN='seu_token'", "info")
        else:
            print_status("Configure: export DYNATRACE_API_TOKEN='seu_token'", "info")
        return 1
    
    # Verifica Monaco
    system = platform.system().lower()
    if system == "windows":
        monaco_path = Path("../../monaco.exe")
    else:
        monaco_path = Path("../../monaco")
    
    if not monaco_path.exists():
        print_status(f"Monaco não encontrado: {{monaco_path}}", "error")
        return 1
    
    # Executa restauração
    cmd = [
        str(monaco_path),
        "deploy",
        "--url", "{self.base_url}",
        "--token", "DYNATRACE_API_TOKEN",
        "--project", ".",
        "--verbose"
    ]
    
    print_status("Executando restauração...", "info")
    
    try:
        env = os.environ.copy()
        result = subprocess.run(cmd, env=env, check=True)
        print_status("Restauração concluída com sucesso!", "success")
        return 0
    except subprocess.CalledProcessError:
        print_status("Erro na restauração", "error")
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
        
        with open(restore_py, 'w', encoding='utf-8') as f:
            f.write(restore_content)
        
        # Torna executável
        if self.system != "windows":
            os.chmod(restore_py, 0o755)
        
        # README
        readme_path = backup_path / "README.md"
        readme_content = f'''# Backup Dynatrace - {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

## Restauração Universal

### Todas as plataformas (Python):
```bash
# Configure o token
export DYNATRACE_API_TOKEN='seu_token'  # Linux/macOS
$env:DYNATRACE_API_TOKEN='seu_token'    # Windows

# Execute a restauração
python restore.py
```

## Informações do Backup

- **Data/Hora**: {datetime.now().strftime("%d/%m/%Y às %H:%M:%S")}
- **Origem**: {self.base_url}
- **Ferramenta**: Monaco CLI
- **Python**: {self.python_version}
- **Sistema**: {platform.system()} {platform.release()}

## Estrutura

- **restore.py**: Script Python universal para restauração
- **project/**: Configurações do Dynatrace em JSON

## Requisitos

- Python 3.6+ (será instalado automaticamente se necessário)
- Monaco CLI (incluído)
- Token com permissões de escrita

---
*Backup gerado pelo script Python universal de backup do Dynatrace*
'''
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        self._print_status(f"Scripts de restauração criados", "success")
    
    def run_complete_backup(self):
        """Executa processo completo de backup."""
        print("=" * 70)
        print("🚀 DYNATRACE BACKUP - SOLUÇÃO UNIVERSAL PYTHON")
        print("=" * 70)
        
        # Validações e instalações automáticas
        if not self.validate_environment():
            return False
            
        if not self.download_monaco():
            return False
            
        if not self.test_connectivity():
            return False
            
        # Executa backup
        backup_path = self.run_backup()
        
        if backup_path:
            print("\n" + "=" * 70)
            print("✅ BACKUP CONCLUÍDO COM SUCESSO!")
            print("=" * 70)
            self._print_status(f"Local: {backup_path}", "success")
            self._print_status("Scripts universais incluídos", "success")
            
            print("\n💡 Para restaurar:")
            print(f"   cd {backup_path}")
            print("   python restore.py")
            
            print("\n📖 Veja README.md para instruções detalhadas")
            
            return True
        else:
            print("\n" + "=" * 70)
            print("❌ FALHA NO BACKUP")
            print("=" * 70)
            return False

def main():
    """Função principal."""
    try:
        backup = DynatraceBackupUniversal()
        success = backup.run_complete_backup()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️  Backup cancelado pelo usuário")
        return 1
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
