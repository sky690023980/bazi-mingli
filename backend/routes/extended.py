# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from backend.services.engine import bazi_pan
from backend.plugins.base import get_registry

router = APIRouter(prefix='/api/extended', tags=['Extended Analysis'])

class PluginQuery(BaseModel):
    pillar_json: Dict[str, Any]
    plugin_name: Optional[str] = None

class FullAnalysisRequest(BaseModel):
    year: int; month: int; day: int; hour: int
    gender: str = 'M'
    location: str = 'Beijing'
    include_plugins: Optional[list] = None

@router.post('/plugins')
def run_plugins(query: PluginQuery):
    try:
        registry = get_registry()
        results = {}
        if query.plugin_name:
            plugin = registry.get(query.plugin_name)
            if not plugin:
                raise HTTPException(status_code=404, detail='Plugin not found')
            results[plugin.name] = plugin.analyze(query.pillar_json)
        else:
            for plugin in registry.list_enabled():
                results[plugin.name] = plugin.analyze(query.pillar_json)
        return {'code': 200, 'msg': 'success', 'data': results}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/full-analysis')
def full_analysis(req: FullAnalysisRequest):
    try:
        pillar_data = bazi_pan(req.year, req.month, req.day, req.hour, req.gender, req.location)
        registry = get_registry()
        plugin_results = {}
        include = req.include_plugins or ['ziwei', 'marriage', 'health', 'qimen']
        for plugin in registry.list_enabled():
            if plugin.name in include:
                try:
                    plugin_results[plugin.name] = plugin.analyze(pillar_data)
                except Exception as e2:
                    plugin_results[plugin.name] = {'error': str(e2)}
        return {'code': 200, 'msg': 'success', 'data': {'pillar': pillar_data, 'plugins': plugin_results}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/plugins/list')
def list_plugins():
    registry = get_registry()
    plugins = [{'name': p.name, 'display_name': p.display_name, 'tags': p.get_tags()} for p in registry.list_all()]
    return {'code': 200, 'msg': 'success', 'data': {'plugins': plugins}}
