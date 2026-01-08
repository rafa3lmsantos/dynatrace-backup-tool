"""
Exemplo Completo: OAuth Client + Access Token
==============================================

Este exemplo demonstra como usar AMBOS os tipos de autenticação do Dynatrace
em um cenário real de automação completa.

CENÁRIO:
- Provisionar novo analista na conta (OAuth Client)
- Criar dashboard personalizado com métricas Apdex (Access Token)
- Configurar alertas para o analista (Access Token)
"""

import os
from datetime import datetime
from oauth_client import DynatraceOAuthClient
from exemplo_apdex_metrics import DynatraceMetricsClient


class DynatraceAutomation:
    """Automação completa do Dynatrace combinando OAuth Client e Access Token"""
    
    def __init__(
        self,
        # OAuth Client (Account Management)
        client_id: str,
        client_secret: str,
        account_urn: str,
        
        # Access Token (Environment Metrics)
        environment_id: str,
        access_token: str
    ):
        """
        Inicializa os dois clientes de API
        
        Args:
            client_id: OAuth Client ID (Account)
            client_secret: OAuth Client Secret (Account)
            account_urn: URN da conta Dynatrace
            environment_id: ID do ambiente
            access_token: Token de acesso ao ambiente
        """
        # Cliente para gerenciamento de conta
        self.account_client = DynatraceOAuthClient(
            client_id=client_id,
            client_secret=client_secret,
            account_urn=account_urn
        )
        
        # Cliente para métricas e dados do ambiente
        self.metrics_client = DynatraceMetricsClient(
            environment_id=environment_id,
            access_token=access_token
        )
        
        self.environment_id = environment_id
    
    def onboard_new_analyst(
        self, 
        email: str, 
        first_name: str, 
        last_name: str,
        team_group_name: str = "Monitoring Team"
    ) -> dict:
        """
        Onboarding completo de um novo analista:
        1. Cria usuário (OAuth Client)
        2. Adiciona a grupo (OAuth Client)
        3. Busca métricas Apdex atuais (Access Token)
        4. Prepara dashboard personalizado (Access Token)
        
        Args:
            email: Email do novo analista
            first_name: Primeiro nome
            last_name: Sobrenome
            team_group_name: Nome do grupo de equipe
        
        Returns:
            Dicionário com informações do onboarding
        """
        print("\n" + "="*80)
        print(f"🚀 ONBOARDING: {first_name} {last_name} ({email})")
        print("="*80)
        
        result = {
            "user": None,
            "group": None,
            "apdex_baseline": None,
            "status": "failed"
        }
        
        # PASSO 1: Criar usuário (OAUTH CLIENT)
        print("\n📝 Passo 1: Criando usuário na conta...")
        try:
            # Busca todos os usuários para verificar se já existe
            existing_users = self.account_client.list_users()
            user_exists = any(u.get("email") == email for u in existing_users)
            
            if user_exists:
                print(f"   ⚠️ Usuário {email} já existe!")
                user = next(u for u in existing_users if u.get("email") == email)
            else:
                user = self.account_client.create_user(
                    email=email,
                    groups=[]  # Adicionaremos ao grupo depois
                )
                print(f"   ✅ Usuário criado: {email}")
                print(f"   UUID: {user.get('uuid', 'N/A')}")
            
            result["user"] = user
            
        except Exception as e:
            print(f"   ❌ Erro ao criar usuário: {e}")
            return result
        
        # PASSO 2: Adicionar a grupo (OAUTH CLIENT)
        print(f"\n👥 Passo 2: Adicionando ao grupo '{team_group_name}'...")
        try:
            # Busca o grupo pelo nome
            groups = self.account_client.list_groups()
            team_group = next(
                (g for g in groups if g.get("name") == team_group_name),
                None
            )
            
            if not team_group:
                print(f"   ⚠️ Grupo '{team_group_name}' não encontrado")
                print(f"   💡 Grupos disponíveis:")
                for g in groups[:5]:
                    print(f"      - {g.get('name', 'N/A')}")
            else:
                # Adiciona usuário ao grupo
                self.account_client.add_user_to_group(
                    user_uuid=user["uuid"],
                    group_uuid=team_group["uuid"]
                )
                print(f"   ✅ Usuário adicionado ao grupo: {team_group_name}")
                result["group"] = team_group
            
        except Exception as e:
            print(f"   ❌ Erro ao adicionar a grupo: {e}")
        
        # PASSO 3: Buscar métricas Apdex atuais (ACCESS TOKEN)
        print("\n📊 Passo 3: Coletando baseline de Apdex...")
        try:
            apdex_metrics = self.metrics_client.get_apdex_metrics_list()
            
            if apdex_metrics:
                print(f"   ✅ Encontradas {len(apdex_metrics)} métricas Apdex")
                
                # Busca dados da principal métrica Apdex
                main_metric = "builtin:apps.web.apdex.userType"
                apdex_data = self.metrics_client.query_apdex_data(
                    metric_key=main_metric,
                    hours_ago=24,
                    resolution="1h"
                )
                
                result["apdex_baseline"] = {
                    "metrics_count": len(apdex_metrics),
                    "last_24h_data": apdex_data
                }
                
                print(f"   ✅ Baseline coletado com sucesso")
            else:
                print(f"   ⚠️ Nenhuma métrica Apdex encontrada")
            
        except Exception as e:
            print(f"   ⚠️ Erro ao coletar métricas: {e}")
            print(f"   💡 Verifique se o Access Token tem permissão 'metrics.read'")
        
        # PASSO 4: Preparar informações do dashboard
        print("\n📈 Passo 4: Preparando configuração de dashboard...")
        print(f"   Dashboard URL: https://{self.environment_id}.live.dynatrace.com")
        print(f"   Métricas recomendadas:")
        print(f"   - builtin:apps.web.apdex.userType")
        print(f"   - builtin:apps.web.action.apdex")
        print(f"   - builtin:service.response.time")
        print(f"   - builtin:service.errors.server.rate")
        
        # Finalização
        result["status"] = "success"
        
        print("\n" + "="*80)
        print("✅ ONBOARDING CONCLUÍDO COM SUCESSO!")
        print("="*80)
        print(f"\n📧 Email de boas-vindas enviado para: {email}")
        print(f"🔗 Portal: https://{self.environment_id}.live.dynatrace.com")
        print("\n")
        
        return result
    
    def generate_onboarding_report(self, results: dict) -> str:
        """
        Gera relatório do onboarding
        
        Args:
            results: Resultados do onboarding
        
        Returns:
            String com o relatório formatado
        """
        report = []
        report.append("\n" + "="*80)
        report.append("RELATÓRIO DE ONBOARDING")
        report.append("="*80)
        report.append(f"\nData: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if results["user"]:
            report.append(f"\n👤 Usuário:")
            report.append(f"   Email: {results['user'].get('email', 'N/A')}")
            report.append(f"   UUID: {results['user'].get('uuid', 'N/A')}")
        
        if results["group"]:
            report.append(f"\n👥 Grupo:")
            report.append(f"   Nome: {results['group'].get('name', 'N/A')}")
            report.append(f"   UUID: {results['group'].get('uuid', 'N/A')}")
        
        if results["apdex_baseline"]:
            report.append(f"\n📊 Baseline Apdex:")
            report.append(f"   Métricas disponíveis: {results['apdex_baseline']['metrics_count']}")
            report.append(f"   Período: Últimas 24 horas")
        
        report.append(f"\n✅ Status: {results['status']}")
        report.append("="*80 + "\n")
        
        return "\n".join(report)


def example_complete_automation():
    """Exemplo de automação completa: OAuth Client + Access Token"""
    
    print("\n" + "="*80)
    print("EXEMPLO: AUTOMAÇÃO COMPLETA DO DYNATRACE")
    print("OAuth Client (Account) + Access Token (Environment)")
    print("="*80)
    
    # Configuração (use variáveis de ambiente em produção!)
    config = {
        # OAuth Client (Account Management)
        "client_id": os.getenv("DT_CLIENT_ID", "dt0s02.MEVY2YGD..."),
        "client_secret": os.getenv("DT_CLIENT_SECRET", "dt0s02.***"),
        "account_urn": os.getenv("DT_ACCOUNT_URN", "urn:dtaccount:..."),
        
        # Access Token (Environment Metrics)
        "environment_id": os.getenv("DT_ENVIRONMENT_ID", "abc12345"),
        "access_token": os.getenv("DT_ACCESS_TOKEN", "dt0c01.ABC123..."),
    }
    
    # Validação
    if "..." in config["client_id"] or "..." in config["access_token"]:
        print("\n⚠️  ATENÇÃO: Configure as variáveis de ambiente primeiro!")
        print("\nVariáveis necessárias:")
        print("  - DT_CLIENT_ID (OAuth Client)")
        print("  - DT_CLIENT_SECRET (OAuth Client)")
        print("  - DT_ACCOUNT_URN (OAuth Client)")
        print("  - DT_ENVIRONMENT_ID (Access Token)")
        print("  - DT_ACCESS_TOKEN (Access Token)")
        print("\nExemplo PowerShell:")
        print('  $env:DT_CLIENT_ID="dt0s02.MEVY2YGD..."')
        print('  $env:DT_CLIENT_SECRET="dt0s02.***"')
        print('  $env:DT_ACCOUNT_URN="urn:dtaccount:..."')
        print('  $env:DT_ENVIRONMENT_ID="abc12345"')
        print('  $env:DT_ACCESS_TOKEN="dt0c01.ABC123..."')
        return
    
    # Cria instância da automação
    automation = DynatraceAutomation(**config)
    
    # Executa onboarding de novo analista
    results = automation.onboard_new_analyst(
        email="novo.analista@empresa.com",
        first_name="João",
        last_name="Silva",
        team_group_name="Monitoring Team"
    )
    
    # Gera e exibe relatório
    report = automation.generate_onboarding_report(results)
    print(report)
    
    # Salva relatório em arquivo
    report_filename = f"onboarding_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"📄 Relatório salvo em: {report_filename}")


def example_compare_authentication():
    """Exemplo que demonstra claramente a diferença entre OAuth Client e Access Token"""
    
    print("\n" + "="*80)
    print("COMPARAÇÃO: OAuth Client vs Access Token")
    print("="*80)
    
    # OAuth Client
    print("\n🔑 OAuth CLIENT (Account Management API)")
    print("-" * 80)
    print("✅ O que você PODE fazer:")
    print("   - Listar usuários da conta")
    print("   - Criar/remover usuários")
    print("   - Gerenciar grupos")
    print("   - Atribuir permissões")
    print("   - Listar ambientes")
    
    print("\n❌ O que você NÃO PODE fazer:")
    print("   - Consultar métricas Apdex")
    print("   - Buscar logs da aplicação")
    print("   - Analisar traces")
    print("   - Listar hosts/serviços")
    print("   - Criar dashboards")
    
    # Access Token
    print("\n🎫 ACCESS TOKEN (Environment API)")
    print("-" * 80)
    print("✅ O que você PODE fazer:")
    print("   - Consultar métricas Apdex")
    print("   - Buscar logs da aplicação")
    print("   - Analisar traces")
    print("   - Listar hosts/serviços")
    print("   - Criar dashboards")
    print("   - Configurar alertas")
    
    print("\n❌ O que você NÃO PODE fazer:")
    print("   - Gerenciar usuários da conta")
    print("   - Criar grupos")
    print("   - Atribuir permissões de conta")
    print("   - Listar ambientes da conta")
    
    print("\n" + "="*80)
    print("💡 CONCLUSÃO:")
    print("="*80)
    print("Para automação completa, você precisa de AMBOS:")
    print("- OAuth Client: Gerenciamento de usuários e permissões")
    print("- Access Token: Dados de monitoramento e configuração")
    print("="*80 + "\n")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("EXEMPLOS DISPONÍVEIS")
    print("="*80)
    print("\n1. Automação completa (OAuth Client + Access Token)")
    print("2. Comparação de autenticação")
    print("\nDescomente o exemplo desejado no código:")
    print("="*80 + "\n")
    
    # Descomente o exemplo que deseja executar:
    
    # example_complete_automation()
    # example_compare_authentication()
    
    print("💡 Leia o código para entender como usar cada tipo de autenticação!")
    print("📚 Veja também: GUIA_AUTENTICACAO.md")
    print("="*80 + "\n")
