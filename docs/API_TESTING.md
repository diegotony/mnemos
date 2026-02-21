# Ejemplos de Pruebas de API - Mnemos

Este archivo contiene ejemplos de `curl` para probar todas las funcionalidades implementadas.

## 🚀 Iniciar el servidor

```bash
cd /path/to/mnemos
uv run uvicorn main:app --reload --port 8000
```

---

## ✅ Pruebas Básicas

### 1. Verificar que el servidor está corriendo

```bash
curl http://localhost:8000/
# Response: {"message":"Hello World"}
```

### 2. Verificar configuración de Google Calendar

```bash
curl http://localhost:8000/api/v1/calendar/health | python3 -m json.tool
```

---

## 📅 Pruebas de Parámetro `date`

### Eventos de hoy (sin priorización)

```bash
curl "http://localhost:8000/api/v1/calendar/events?date=today" | python3 -m json.tool
```

### Eventos de mañana

```bash
curl "http://localhost:8000/api/v1/calendar/events?date=tomorrow" | python3 -m json.tool
```

### Eventos de fecha específica

```bash
curl "http://localhost:8000/api/v1/calendar/events?date=2026-02-25" | python3 -m json.tool
```

### Fecha inválida (debería retornar error 400)

```bash
curl "http://localhost:8000/api/v1/calendar/events?date=invalid" | python3 -m json.tool
# Response: {"detail": "Invalid date format. Use 'today', 'tomorrow', or 'YYYY-MM-DD'"}
```

---

## 🎯 Pruebas de Priorización

### Eventos de hoy priorizados

```bash
curl "http://localhost:8000/api/v1/calendar/events?date=today&prioritized=true" | python3 -m json.tool
```

### Solo ver contadores

```bash
curl -s "http://localhost:8000/api/v1/calendar/events?date=today&prioritized=true" | \
  python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data['counts'], indent=2))"
```

### Solo ver configuración

```bash
curl -s "http://localhost:8000/api/v1/calendar/events?date=today&prioritized=true" | \
  python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data['config'], indent=2))"
```

---

## 🏷️ Pruebas de Filtro por Categoría (Case-Insensitive)

### Mayúsculas

```bash
curl "http://localhost:8000/api/v1/calendar/events?category=TRABAJO" | \
  python3 -c "import sys, json; data=json.load(sys.stdin); print(f'Total: {len(data)}'); [print(f\"- {e['summary']}: {e['category']}\") for e in data]"
```

### Minúsculas

```bash
curl "http://localhost:8000/api/v1/calendar/events?category=trabajo" | \
  python3 -c "import sys, json; data=json.load(sys.stdin); print(f'Total: {len(data)}'); [print(f\"- {e['summary']}: {e['category']}\") for e in data]"
```

### Mixtas

```bash
curl "http://localhost:8000/api/v1/calendar/events?category=Trabajo" | \
  python3 -c "import sys, json; data=json.load(sys.stdin); print(f'Total: {len(data)}'); [print(f\"- {e['summary']}: {e['category']}\") for e in data]"
```

### Categoría inexistente (retorna array vacío)

```bash
curl "http://localhost:8000/api/v1/calendar/events?category=INVALID" | \
  python3 -c "import sys, json; data=json.load(sys.stdin); print(f'Total: {len(data)}')"
# Response: Total: 0
```

---

## 🎨 Pruebas de Combinaciones

### Caso 1: Todo de hoy priorizado

```bash
curl "http://localhost:8000/api/v1/calendar/events?date=today&prioritized=true" | python3 -m json.tool
```

### Caso 2: Solo rutinas de hoy

```bash
curl "http://localhost:8000/api/v1/calendar/events?date=today&category=RUTINA" | python3 -m json.tool
```

### Caso 3: Solo TRABAJO de hoy priorizado

```bash
curl "http://localhost:8000/api/v1/calendar/events?date=today&category=TRABAJO&prioritized=true" | python3 -m json.tool
```

### Caso 4: Rutinas priorizadas (edge case)

```bash
curl "http://localhost:8000/api/v1/calendar/events?category=RUTINA&prioritized=true" | python3 -m json.tool
```

### Caso 5: Backward compatibility (sin priorización)

```bash
curl "http://localhost:8000/api/v1/calendar/events?date=today" | \
  python3 -c "import sys, json; data=json.load(sys.stdin); print(f'Tipo: {type(data).__name__}'); print(f'Total: {len(data)}')"
# Response: Tipo: list, Total: X
```

---

## 🔍 Pruebas de Casos Edge

### Sin eventos

```bash
# Si no hay eventos en el rango
curl "http://localhost:8000/api/v1/calendar/events?date=2030-01-01&prioritized=true" | python3 -m json.tool
```

### Todos los eventos son de alta prioridad

```bash
# Crear eventos solo de TRABAJO con priority=critical
# Luego consultar:
curl "http://localhost:8000/api/v1/calendar/events?date=today&prioritized=true" | \
  python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"High: {data['counts']['high_priority']}, Regular: {data['counts']['regular']}, Routines: {data['counts']['routines']}\")"
```

---

## 📊 Pruebas de Análisis Rápido

### Contar eventos por categoría

```bash
curl -s "http://localhost:8000/api/v1/calendar/events?date=today&prioritized=true" | \
  python3 -c "import sys, json; data=json.load(sys.stdin); print('Eventos por categoría:'); [print(f'  {k}: {v}') for k,v in data['counts']['by_category'].items()]"
```

### Ver solo eventos de alta prioridad

```bash
curl -s "http://localhost:8000/api/v1/calendar/events?date=today&prioritized=true" | \
  python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"Alta prioridad ({len(data['high_priority'])} eventos):\"); [print(f\"  - {e['start_datetime'][11:16]} {e['summary']}\") for e in data['high_priority']]"
```

---

## 🧪 Script de Prueba Completo

Guarda esto en `test_api.sh`:

```bash
#!/bin/bash

API_URL="http://localhost:8000/api/v1/calendar/events"

echo "=== Prueba 1: Fecha inválida (debe dar error 400) ==="
curl -s "$API_URL?date=invalid" | python3 -m json.tool
echo ""

echo "=== Prueba 2: Eventos de hoy sin priorización (debe retornar array) ==="
curl -s "$API_URL?date=today" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'Tipo: {type(data).__name__}, Total: {len(data)}')"
echo ""

echo "=== Prueba 3: Eventos de hoy priorizados (debe retornar objeto con grupos) ==="
curl -s "$API_URL?date=today&prioritized=true" | python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data['counts'], indent=2))"
echo ""

echo "=== Prueba 4: Filtro case-insensitive ==="
echo "TRABAJO (mayúsculas):"
curl -s "$API_URL?category=TRABAJO" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'Total: {len(data)}')"
echo "trabajo (minúsculas):"
curl -s "$API_URL?category=trabajo" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'Total: {len(data)}')"
echo ""

echo "=== Prueba 5: Categoría inexistente (debe retornar array vacío) ==="
curl -s "$API_URL?category=INVALID" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'Total: {len(data)}')"
echo ""

echo "=== Prueba 6: Combinación - TRABAJO de hoy priorizado ==="
curl -s "$API_URL?date=today&category=TRABAJO&prioritized=true" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"High: {data['counts']['high_priority']}, Regular: {data['counts']['regular']}, Total: {data['counts']['total']}\")"
echo ""

echo "✅ Todas las pruebas completadas"
```

Ejecutar:

```bash
chmod +x test_api.sh
./test_api.sh
```

---

## 🐍 Script de Prueba en Python

Guarda esto en `test_api.py`:

```python
#!/usr/bin/env python3
"""
Script de pruebas para la API de Mnemos.
"""

import requests
import json

API_URL = "http://localhost:8000/api/v1/calendar/events"

def test_invalid_date():
    """Prueba: Fecha inválida debe retornar 400"""
    print("=== Prueba 1: Fecha inválida ===")
    response = requests.get(API_URL, params={"date": "invalid"})
    assert response.status_code == 400
    print(f"✅ Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print()

def test_today_no_prioritization():
    """Prueba: Eventos de hoy sin priorización retorna array"""
    print("=== Prueba 2: Hoy sin priorización ===")
    response = requests.get(API_URL, params={"date": "today"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print(f"✅ Status: {response.status_code}")
    print(f"   Tipo: {type(data).__name__}")
    print(f"   Total eventos: {len(data)}")
    print()

def test_today_prioritized():
    """Prueba: Eventos de hoy priorizados retorna objeto con grupos"""
    print("=== Prueba 3: Hoy priorizado ===")
    response = requests.get(API_URL, params={"date": "today", "prioritized": True})
    assert response.status_code == 200
    data = response.json()
    assert "high_priority" in data
    assert "regular" in data
    assert "routines" in data
    assert "counts" in data
    assert "config" in data
    print(f"✅ Status: {response.status_code}")
    print(f"   Contadores: {json.dumps(data['counts'], indent=4)}")
    print()

def test_case_insensitive_category():
    """Prueba: Filtro por categoría es case-insensitive"""
    print("=== Prueba 4: Categoría case-insensitive ===")
    
    # Mayúsculas
    r1 = requests.get(API_URL, params={"category": "TRABAJO"})
    count1 = len(r1.json())
    
    # Minúsculas
    r2 = requests.get(API_URL, params={"category": "trabajo"})
    count2 = len(r2.json())
    
    # Mixtas
    r3 = requests.get(API_URL, params={"category": "Trabajo"})
    count3 = len(r3.json())
    
    assert count1 == count2 == count3
    print(f"✅ TRABAJO: {count1} eventos")
    print(f"   trabajo: {count2} eventos")
    print(f"   Trabajo: {count3} eventos")
    print(f"   Todos iguales: {count1 == count2 == count3}")
    print()

def test_invalid_category():
    """Prueba: Categoría inexistente retorna array vacío"""
    print("=== Prueba 5: Categoría inexistente ===")
    response = requests.get(API_URL, params={"category": "INVALID"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0
    print(f"✅ Status: {response.status_code}")
    print(f"   Total: {len(data)} (array vacío)")
    print()

def test_combination():
    """Prueba: Combinación de filtros"""
    print("=== Prueba 6: Combinación - TRABAJO de hoy priorizado ===")
    response = requests.get(API_URL, params={
        "date": "today",
        "category": "TRABAJO",
        "prioritized": True
    })
    assert response.status_code == 200
    data = response.json()
    print(f"✅ Status: {response.status_code}")
    print(f"   Alta prioridad: {data['counts']['high_priority']}")
    print(f"   Regular: {data['counts']['regular']}")
    print(f"   Total: {data['counts']['total']}")
    print()

if __name__ == "__main__":
    try:
        test_invalid_date()
        test_today_no_prioritization()
        test_today_prioritized()
        test_case_insensitive_category()
        test_invalid_category()
        test_combination()
        print("✅ TODAS LAS PRUEBAS PASARON")
    except AssertionError as e:
        print(f"❌ ERROR: {e}")
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {e}")
```

Ejecutar:

```bash
chmod +x test_api.py
python3 test_api.py
```

---

## 📝 Notas

- Los errores LSP en `routers/calendar.py` son warnings de type checking, no afectan la ejecución
- Todas las funcionalidades están implementadas y probadas
- La configuración es flexible mediante variables de entorno
- Backward compatibility está garantizada (sin `prioritized=true` retorna array plano)
