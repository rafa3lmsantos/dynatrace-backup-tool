"""
Exemplo: Como obter métricas Apdex do Dynatrace
================================================

IMPORTANTE: Este exemplo usa Environment Access Token (não OAuth Client)
Para métricas Apdex, você precisa de um token de ambiente com permissões de leitura.

Como criar um Environment Access Token:
1. Acesse seu ambiente Dynatrace: https://{your-environment}.live.dynatrace.com
2. Vá em Settings > Access tokens
3. Clique em "Generate new token"
4. Dê um nome (ex: "Apdex Metrics Reader")
5. Marque a permissão: "Read metrics" (metrics.read)
6. Clique em "Generate token" e copie o valor
"""

import requests
import json
from datetime import datetime, timedelta
import os

class DynatraceMetricsClient:
    """Cliente para acessar métricas do Dynatrace (incluindo Apdex)"""
    
    def __init__(self, environment_id: str, access_token: str):
        """
        Inicializa o cliente de métricas
        
        Args:
            environment_id: ID do seu ambiente (ex: "abc12345")
            access_token: Environment Access Token com permissão metrics.read
        """
        self.environment_id = environment_id
        self.access_token = access_token
        self.base_url = f"https://{environment_id}.live.dynatrace.com/api/v2"
        
    def _make_request(self, endpoint: str, params: dict = None) -> dict:
        """Faz requisição à API de métricas"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Api-Token {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"❌ Erro HTTP: {e}")
            print(f"Resposta: {response.text}")
            raise
        except Exception as e:
            print(f"❌ Erro: {e}")
            raise
    
    def list_all_metrics(self, filter_text: str = None) -> list:
        """
        Lista todas as métricas disponíveis
        
        Args:
            filter_text: Filtro opcional (ex: "apdex")
        
        Returns:
            Lista de métricas disponíveis
        """
        params = {"pageSize": 500}
        if filter_text:
            params["text"] = filter_text
            
        result = self._make_request("/metrics", params)
        return result.get("metrics", [])
    
    def get_apdex_metrics_list(self) -> list:
        """Retorna todas as métricas Apdex disponíveis"""
        return self.list_all_metrics("apdex")
    
    def get_metric_details(self, metric_key: str) -> dict:
        """
        Obtém detalhes de uma métrica específica
        
        Args:
            metric_key: Nome da métrica (ex: "builtin:apps.web.apdex.userType")
        
        Returns:
            Detalhes completos da métrica
        """
        return self._make_request(f"/metrics/{metric_key}")
    
    def query_apdex_data(
        self, 
        metric_key: str, 
        hours_ago: int = 1,
        resolution: str = "5m"
    ) -> dict:
        """
        Consulta dados de uma métrica Apdex
        
        Args:
            metric_key: Nome da métrica Apdex
            hours_ago: Quantas horas atrás buscar dados (padrão: 1 hora)
            resolution: Resolução dos dados (1m, 5m, 1h, etc.)
        
        Returns:
            Dados da métrica no período especificado
        """
        # Calcula timestamps
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours_ago)
        
        # Formata timestamps para a API (ISO 8601)
        from_timestamp = start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        to_timestamp = end_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        
        params = {
            "metricSelector": metric_key,
            "from": from_timestamp,
            "to": to_timestamp,
            "resolution": resolution
        }
        
        return self._make_request("/metrics/query", params)


def example_list_apdex_metrics():
    """Exemplo 1: Listar todas as métricas Apdex disponíveis"""
    print("\n" + "="*80)
    print("EXEMPLO 1: Listar todas as métricas Apdex disponíveis")
    print("="*80)
    
    # Configure suas credenciais aqui
    environment_id = os.getenv("DT_ENVIRONMENT_ID", "abc12345")
    access_token = os.getenv("DT_ACCESS_TOKEN", "dt0c01.ABC123...")
    
    client = DynatraceMetricsClient(environment_id, access_token)
    
    try:
        apdex_metrics = client.get_apdex_metrics_list()
        
        print(f"\n✅ Encontradas {len(apdex_metrics)} métricas Apdex:")
        print("-" * 80)
        
        for metric in apdex_metrics:
            print(f"\n📊 {metric['metricId']}")
            print(f"   Descrição: {metric.get('displayName', 'N/A')}")
            print(f"   Unidade: {metric.get('unit', 'N/A')}")
            print(f"   Dimensões: {', '.join(metric.get('dimensionDefinitions', []))}")
            
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        print("\n💡 Dica: Verifique se você configurou as variáveis de ambiente:")
        print("   - DT_ENVIRONMENT_ID: ID do seu ambiente")
        print("   - DT_ACCESS_TOKEN: Token de acesso com permissão metrics.read")


def example_get_apdex_details():
    """Exemplo 2: Obter detalhes de uma métrica Apdex específica"""
    print("\n" + "="*80)
    print("EXEMPLO 2: Detalhes de uma métrica Apdex específica")
    print("="*80)
    
    environment_id = os.getenv("DT_ENVIRONMENT_ID", "abc12345")
    access_token = os.getenv("DT_ACCESS_TOKEN", "dt0c01.ABC123...")
    
    client = DynatraceMetricsClient(environment_id, access_token)
    
    # Métrica de exemplo: Apdex por tipo de usuário em web apps
    metric_key = "builtin:apps.web.apdex.userType"
    
    try:
        details = client.get_metric_details(metric_key)
        
        print(f"\n📊 Métrica: {metric_key}")
        print(f"   Nome: {details.get('displayName', 'N/A')}")
        print(f"   Descrição: {details.get('description', 'N/A')}")
        print(f"   Unidade: {details.get('unit', 'N/A')}")
        print(f"   Tipo de agregação: {', '.join(details.get('aggregationTypes', []))}")
        
        if 'dimensionDefinitions' in details:
            print(f"\n   Dimensões disponíveis:")
            for dim in details['dimensionDefinitions']:
                print(f"   - {dim['key']}: {dim.get('displayName', 'N/A')}")
                
    except Exception as e:
        print(f"\n❌ Erro: {e}")


def example_query_apdex_values():
    """Exemplo 3: Consultar valores reais de Apdex"""
    print("\n" + "="*80)
    print("EXEMPLO 3: Consultar valores de Apdex da última hora")
    print("="*80)
    
    environment_id = os.getenv("DT_ENVIRONMENT_ID", "abc12345")
    access_token = os.getenv("DT_ACCESS_TOKEN", "dt0c01.ABC123...")
    
    client = DynatraceMetricsClient(environment_id, access_token)
    
    # Consulta Apdex por tipo de usuário
    metric_key = "builtin:apps.web.apdex.userType"
    
    try:
        data = client.query_apdex_data(metric_key, hours_ago=1, resolution="5m")
        
        print(f"\n📊 Dados de Apdex:")
        print(f"   Métrica: {metric_key}")
        
        if 'result' in data:
            for result in data['result']:
                metric_id = result.get('metricId', 'N/A')
                
                print(f"\n   Aplicação: {result.get('data', [{}])[0].get('dimensions', {})}")
                
                # Exibe os valores coletados
                if 'data' in result:
                    for data_point in result['data']:
                        print(f"\n   Valores coletados:")
                        for timestamp, values in zip(data_point.get('timestamps', []), 
                                                     data_point.get('values', [])):
                            # Converte timestamp Unix para data legível
                            dt = datetime.fromtimestamp(timestamp / 1000)
                            print(f"   {dt.strftime('%Y-%m-%d %H:%M:%S')} - Apdex: {values}")
        else:
            print("\n   ⚠️ Nenhum dado encontrado para o período especificado")
            
    except Exception as e:
        print(f"\n❌ Erro: {e}")


def example_compare_apdex_by_app():
    """Exemplo 4: Comparar Apdex entre diferentes aplicações"""
    print("\n" + "="*80)
    print("EXEMPLO 4: Comparar Apdex entre aplicações")
    print("="*80)
    
    environment_id = os.getenv("DT_ENVIRONMENT_ID", "abc12345")
    access_token = os.getenv("DT_ACCESS_TOKEN", "dt0c01.ABC123...")
    
    client = DynatraceMetricsClient(environment_id, access_token)
    
    # Usa filtro mais abrangente para capturar todas as apps
    metric_key = "builtin:apps.web.apdex.userType:filter(eq(\"dt.entity.application\"))"
    
    try:
        data = client.query_apdex_data(metric_key, hours_ago=24, resolution="1h")
        
        print(f"\n📊 Comparação de Apdex por aplicação (últimas 24h):")
        
        if 'result' in data:
            app_apdex = {}
            
            for result in data['result']:
                if 'data' in result:
                    for data_point in result['data']:
                        dimensions = data_point.get('dimensions', {})
                        app_name = dimensions.get('dt.entity.application', 'Desconhecida')
                        
                        # Calcula média do Apdex
                        values = data_point.get('values', [])
                        if values:
                            avg_apdex = sum(values) / len(values)
                            app_apdex[app_name] = avg_apdex
            
            # Ordena por Apdex (maior para menor)
            sorted_apps = sorted(app_apdex.items(), key=lambda x: x[1], reverse=True)
            
            print(f"\n   Ranking de Apdex:")
            for i, (app, apdex) in enumerate(sorted_apps, 1):
                emoji = "🟢" if apdex >= 0.94 else "🟡" if apdex >= 0.85 else "🔴"
                print(f"   {i}. {emoji} {app}: {apdex:.3f}")
                
        else:
            print("\n   ⚠️ Nenhum dado encontrado")
            
    except Exception as e:
        print(f"\n❌ Erro: {e}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("COMO OBTER MÉTRICAS APDEX DO DYNATRACE")
    print("="*80)
    
    print("\n⚙️  Configuração necessária:")
    print("1. Crie um Environment Access Token no Dynatrace")
    print("2. Configure as variáveis de ambiente:")
    print("   - DT_ENVIRONMENT_ID=seu_environment_id")
    print("   - DT_ACCESS_TOKEN=seu_access_token")
    print("\n   Exemplo no PowerShell:")
    print('   $env:DT_ENVIRONMENT_ID="abc12345"')
    print('   $env:DT_ACCESS_TOKEN="dt0c01.ABC123..."')
    
    print("\n" + "="*80)
    
    # Descomente os exemplos que deseja executar:
    
    # example_list_apdex_metrics()
    # example_get_apdex_details()
    # example_query_apdex_values()
    # example_compare_apdex_by_app()
    
    print("\n💡 Descomente os exemplos acima para executá-los!")
    print("="*80 + "\n")
