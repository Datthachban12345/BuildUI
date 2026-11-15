from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field

A2UIVersion = Literal["1.0"]

class ComponentNode(BaseModel):
    id: str
    type: str
    parentId: Optional[str] = None
    props: Dict[str, Any] = Field(default_factory=dict)
    children: List[str] = Field(default_factory=list)

class SurfaceLayoutConfig(BaseModel):
    type: Optional[Literal["standard", "fullscreen", "modal", "drawer"]] = "standard"
    theme: Optional[Dict[str, Any]] = Field(default_factory=lambda: {"mode": "dark", "primaryColor": "#3b82f6"})

class CreateSurfaceMessage(BaseModel):
    version: A2UIVersion = "1.0"
    type: Literal["createSurface"] = "createSurface"
    surfaceId: str
    catalogId: str = "astryx-web-v1"
    title: Optional[str] = "Generated Website"
    layout: Optional[SurfaceLayoutConfig] = Field(default_factory=SurfaceLayoutConfig)

class UpdateComponentsMessage(BaseModel):
    version: A2UIVersion = "1.0"
    type: Literal["updateComponents"] = "updateComponents"
    surfaceId: str
    components: List[ComponentNode]

class UpdateDataModelMessage(BaseModel):
    version: A2UIVersion = "1.0"
    type: Literal["updateDataModel"] = "updateDataModel"
    surfaceId: str
    operation: Literal["merge", "set", "delete"] = "merge"
    path: Optional[str] = None
    value: Any

class DeleteSurfaceMessage(BaseModel):
    version: A2UIVersion = "1.0"
    type: Literal["deleteSurface"] = "deleteSurface"
    surfaceId: str

class SurfaceActionMessage(BaseModel):
    version: A2UIVersion = "1.0"
    type: Literal["surfaceAction"] = "surfaceAction"
    surfaceId: str
    componentId: str
    action: str
    payload: Optional[Dict[str, Any]] = Field(default_factory=dict)

A2UIMessage = Union[
    CreateSurfaceMessage,
    UpdateComponentsMessage,
    UpdateDataModelMessage,
    DeleteSurfaceMessage,
    SurfaceActionMessage,
]

class GenerateWebsiteRequest(BaseModel):
    prompt: Optional[str] = None
    raw_data: Optional[Union[Dict[str, Any], List[Any], str]] = None
    catalog_id: str = "astryx-web-v1"
