export type Point = [number, number];

export type TerrainInput = {
  width_m: number;
  length_m: number;
  total_area_m2?: number;
  terrain_shape: "rectangle";
  slope_percent: number;
  climate: string;
  soil_type: string;
  water_availability: string;
  existing_vegetation: string;
  existing_structures: string;
};

export type ParkRequirements = {
  conservation_percentage: number;
  recreation_percentage: number;
  education_percentage: number;
  accessibility_required: boolean;
  water_features_required: boolean;
  pedestrian_paths_required: boolean;
  bicycle_paths_required: boolean;
  lighting_required: boolean;
  estimated_budget?: number | null;
  target_biodiversity: number;
  maintenance_level: "low" | "medium" | "high";
};

export type Project = {
  id: string;
  name: string;
  description: string;
  terrain: TerrainInput;
  requirements: ParkRequirements;
  created_at: string;
  updated_at: string;
};

export type ZoneType =
  | "CONSERVATION" | "FOREST" | "MEADOW" | "WETLAND" | "WATER" | "RECREATION"
  | "EDUCATION" | "PLAYGROUND" | "REST_AREA" | "PATH" | "BIKE_PATH" | "SERVICE"
  | "PARKING" | "ENTRANCE" | "BUILDING";

export type Zone = { id: string; type: ZoneType; polygon: Point[]; area_m2: number; percentage: number; priority: number; metadata: Record<string, unknown> };
export type ParkPath = { id: string; type: "PATH" | "BIKE_PATH"; coordinates: Point[]; length_m: number; width_m: number; metadata: Record<string, unknown> };
export type Metrics = {
  total_area_m2: number; conservation_area_m2: number; conservation_percentage: number;
  recreation_area_m2: number; recreation_percentage: number; water_area_m2: number;
  path_length_m: number; bicycle_path_length_m: number; zone_count: number;
  connectivity_index: number; ecological_index: number; overall_score: number; estimated_cost: number;
};
export type ValidationResult = { valid: boolean; errors: string[]; warnings: string[]; score: number };
export type Design = {
  id: string; project_id: string; alternative: string; boundary: Point[]; zones: Zone[];
  paths: ParkPath[]; metrics: Metrics; validation: ValidationResult; score: number; summary: string;
};

export type ProjectDraft = { name: string; description: string; terrain: TerrainInput; requirements: ParkRequirements };

export const defaultDraft: ProjectDraft = {
  name: "Nuevo parque ecológico",
  description: "Propuesta preliminar de EcoPark AI",
  terrain: {
    width_m: 100, length_m: 100, terrain_shape: "rectangle", slope_percent: 5,
    climate: "temperate", soil_type: "loam", water_availability: "medium",
    existing_vegetation: "none", existing_structures: "none",
  },
  requirements: {
    conservation_percentage: 35, recreation_percentage: 20, education_percentage: 8,
    accessibility_required: true, water_features_required: true, pedestrian_paths_required: true,
    bicycle_paths_required: false, lighting_required: false, estimated_budget: null,
    target_biodiversity: 7, maintenance_level: "medium",
  },
};
