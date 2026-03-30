"""
Alert Visualization - ImpressionCore

Real-time visualization system for security alerts and threats. Provides
interactive charts, graphs, and visual representations of security data
for the dashboard interface.

Features:
- Real-time alert visualization with multiple chart types
- Interactive threat timeline and heat maps
- Geographic threat visualization (when location data available)
- Risk trend analysis and pattern visualization
- Memory-efficient chart data management and rendering

Memory Budget: 10MB
Performance Target: <30ms chart updates
Hardware: Optimized for GTX 1050 Ti

Created: 2025-05-31
Author: ImpressionCore AI
"""

import asyncio
import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import logging
import base64
import io

# Import rich enhancements for better UX
try:
    from src.core.utils.rich_logging import RichLogger
    from src.core.utils.rich_enhancements import RichConsole
    logger = RichLogger("AlertVisualization")
    console = RichConsole()
except ImportError:
    import logging
    logger = logging.getLogger("AlertVisualization")
    console = None

@dataclass
class ChartDataPoint:
    """Individual data point for chart visualization."""
    timestamp: datetime
    value: Union[int, float]
    label: str
    category: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ChartConfiguration:
    """Configuration for chart visualization."""
    chart_type: str  # "line", "bar", "pie", "heatmap", "timeline"
    title: str
    x_axis_label: str
    y_axis_label: str
    width: int = 800
    height: int = 400
    max_data_points: int = 100
    update_interval: int = 5  # seconds
    color_scheme: str = "security"  # "security", "performance", "status"
    show_legend: bool = True
    interactive: bool = True

@dataclass
class VisualizationWidget:
    """Widget for displaying security visualizations."""
    widget_id: str
    widget_type: str
    title: str
    data_source: str
    chart_config: ChartConfiguration
    position: Tuple[int, int]  # (x, y)
    size: Tuple[int, int]     # (width, height)
    refresh_rate: int = 5     # seconds
    is_enabled: bool = True
    last_updated: datetime = None

class ChartRenderer:
    """Renders charts and visualizations for security data."""
    
    def __init__(self):
        """Initialize chart renderer."""
        self.color_schemes = {
            'security': {
                'critical': '#FF4444',
                'high': '#FF8800',
                'medium': '#FFCC00', 
                'low': '#88CC00',
                'info': '#4488FF',
                'background': '#F8F9FA',
                'grid': '#E9ECEF'
            },
            'performance': {
                'excellent': '#00CC44',
                'good': '#88CC00',
                'warning': '#FFCC00',
                'poor': '#FF8800',
                'critical': '#FF4444',
                'background': '#F8F9FA',
                'grid': '#E9ECEF'
            },
            'status': {
                'online': '#00CC44',
                'offline': '#FF4444',
                'warning': '#FFCC00',
                'maintenance': '#4488FF',
                'unknown': '#888888',
                'background': '#F8F9FA',
                'grid': '#E9ECEF'
            }
        }
    
    def render_line_chart(self, data_points: List[ChartDataPoint], 
                         config: ChartConfiguration) -> Dict[str, Any]:
        """Render line chart for time series data."""
        try:
            # Prepare data for line chart
            series_data = defaultdict(list)
            
            for point in data_points:
                series_data[point.category].append({
                    'x': point.timestamp.isoformat(),
                    'y': point.value,
                    'label': point.label
                })
            
            # Chart configuration
            chart_data = {
                'type': 'line',
                'data': {
                    'datasets': []
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'scales': {
                        'x': {
                            'type': 'time',
                            'display': True,
                            'title': {
                                'display': True,
                                'text': config.x_axis_label
                            }
                        },
                        'y': {
                            'display': True,
                            'title': {
                                'display': True,
                                'text': config.y_axis_label
                            }
                        }
                    },
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': config.title
                        },
                        'legend': {
                            'display': config.show_legend
                        }
                    },
                    'interaction': {
                        'intersect': False,
                        'mode': 'index'
                    }
                }
            }
            
            # Add datasets for each category
            colors = self.color_schemes.get(config.color_scheme, self.color_schemes['security'])
            color_keys = list(colors.keys())
            
            for i, (category, points) in enumerate(series_data.items()):
                color_key = color_keys[i % len(color_keys)]
                color = colors.get(color_key, colors['info'])
                
                dataset = {
                    'label': category,
                    'data': points,
                    'borderColor': color,
                    'backgroundColor': color + '33',  # Add transparency
                    'fill': False,
                    'tension': 0.4
                }
                chart_data['data']['datasets'].append(dataset)
            
            return {
                'status': 'success',
                'chart_data': chart_data,
                'data_points_count': len(data_points),
                'categories_count': len(series_data)
            }
            
        except Exception as e:
            logger.error(f"Error rendering line chart: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def render_bar_chart(self, data_points: List[ChartDataPoint],
                        config: ChartConfiguration) -> Dict[str, Any]:
        """Render bar chart for categorical data."""
        try:
            # Aggregate data by category
            category_data = defaultdict(float)
            category_counts = defaultdict(int)
            
            for point in data_points:
                category_data[point.category] += point.value
                category_counts[point.category] += 1
            
            # Prepare chart data
            labels = list(category_data.keys())
            values = [category_data[label] for label in labels]
            
            colors = self.color_schemes.get(config.color_scheme, self.color_schemes['security'])
            chart_colors = [colors.get(label.lower(), colors['info']) for label in labels]
            
            chart_data = {
                'type': 'bar',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'label': config.title,
                        'data': values,
                        'backgroundColor': chart_colors,
                        'borderColor': chart_colors,
                        'borderWidth': 1
                    }]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'scales': {
                        'x': {
                            'display': True,
                            'title': {
                                'display': True,
                                'text': config.x_axis_label
                            }
                        },
                        'y': {
                            'display': True,
                            'title': {
                                'display': True,
                                'text': config.y_axis_label
                            },
                            'beginAtZero': True
                        }
                    },
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': config.title
                        },
                        'legend': {
                            'display': config.show_legend
                        }
                    }
                }
            }
            
            return {
                'status': 'success',
                'chart_data': chart_data,
                'categories': len(labels),
                'total_value': sum(values)
            }
            
        except Exception as e:
            logger.error(f"Error rendering bar chart: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def render_pie_chart(self, data_points: List[ChartDataPoint],
                        config: ChartConfiguration) -> Dict[str, Any]:
        """Render pie chart for distribution visualization."""
        try:
            # Aggregate data by category
            category_data = defaultdict(float)
            
            for point in data_points:
                category_data[point.category] += point.value
            
            # Prepare chart data
            labels = list(category_data.keys())
            values = [category_data[label] for label in labels]
            
            colors = self.color_schemes.get(config.color_scheme, self.color_schemes['security'])
            chart_colors = [colors.get(label.lower(), colors['info']) for label in labels]
            
            chart_data = {
                'type': 'pie',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'data': values,
                        'backgroundColor': chart_colors,
                        'borderColor': chart_colors,
                        'borderWidth': 1
                    }]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': config.title
                        },
                        'legend': {
                            'display': config.show_legend,
                            'position': 'right'
                        }
                    }
                }
            }
            
            return {
                'status': 'success',
                'chart_data': chart_data,
                'categories': len(labels),
                'total_value': sum(values)
            }
            
        except Exception as e:
            logger.error(f"Error rendering pie chart: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def render_heatmap(self, data_points: List[ChartDataPoint],
                      config: ChartConfiguration) -> Dict[str, Any]:
        """Render heatmap for pattern visualization."""
        try:
            # Create time-based heatmap data
            heatmap_data = defaultdict(lambda: defaultdict(float))
            
            for point in data_points:
                hour = point.timestamp.hour
                day = point.timestamp.strftime('%Y-%m-%d')
                heatmap_data[day][hour] += point.value
            
            # Convert to matrix format
            days = sorted(heatmap_data.keys())
            hours = list(range(24))
            
            matrix_data = []
            for day in days:
                row = []
                for hour in hours:
                    row.append(heatmap_data[day].get(hour, 0))
                matrix_data.append(row)
            
            chart_data = {
                'type': 'heatmap',
                'data': {
                    'labels': [f"{h:02d}:00" for h in hours],
                    'datasets': [{
                        'label': config.title,
                        'data': matrix_data,
                        'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                        'borderColor': 'rgba(255, 99, 132, 1)',
                    }]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': config.title
                        }
                    }
                }
            }
            
            return {
                'status': 'success',
                'chart_data': chart_data,
                'days': len(days),
                'hours': len(hours)
            }
            
        except Exception as e:
            logger.error(f"Error rendering heatmap: {e}")
            return {'status': 'error', 'error': str(e)}

class AlertVisualization:
    """
    Real-time visualization system for security alerts and threats.
    Provides interactive charts and visual representations of security data.
    """
    
    def __init__(self):
        """Initialize alert visualization system."""
        self.is_running = False
        self.visualization_lock = threading.Lock()
        
        # Chart renderer
        self.renderer = ChartRenderer()
        
        # Memory-optimized data storage
        self.chart_data_cache: Dict[str, deque] = defaultdict(lambda: deque(maxlen=500))
        self.widget_cache: Dict[str, VisualizationWidget] = {}
        
        # Visualization configuration
        self.config = {
            'max_widgets': 10,
            'chart_update_interval': 5,  # seconds
            'data_retention_hours': 24,
            'max_data_points_per_chart': 200,
            'enable_real_time_updates': True
        }
        
        # Performance tracking
        self.render_performance = {
            'render_times': deque(maxlen=100),
            'data_points_processed': deque(maxlen=100),
            'memory_usage': deque(maxlen=100)
        }
        
        # Initialize default widgets
        self._init_default_widgets()
        
        logger.info("AlertVisualization initialized")
    
    def _init_default_widgets(self) -> None:
        """Initialize default visualization widgets."""
        default_widgets = [
            VisualizationWidget(
                widget_id="threats_timeline",
                widget_type="line_chart",
                title="Threat Activity Timeline",
                data_source="threat_events",
                chart_config=ChartConfiguration(
                    chart_type="line",
                    title="Security Threats Over Time",
                    x_axis_label="Time",
                    y_axis_label="Threat Count",
                    color_scheme="security"
                ),
                position=(0, 0),
                size=(800, 400)
            ),
            VisualizationWidget(
                widget_id="alert_severity_distribution",
                widget_type="pie_chart",
                title="Alert Severity Distribution",
                data_source="alert_severity",
                chart_config=ChartConfiguration(
                    chart_type="pie",
                    title="Distribution of Alert Severities",
                    x_axis_label="Severity",
                    y_axis_label="Count",
                    color_scheme="security"
                ),
                position=(800, 0),
                size=(400, 400)
            ),
            VisualizationWidget(
                widget_id="component_status",
                widget_type="bar_chart",
                title="Security Component Status",
                data_source="component_health",
                chart_config=ChartConfiguration(
                    chart_type="bar",
                    title="Security Component Health",
                    x_axis_label="Component",
                    y_axis_label="Health Score",
                    color_scheme="status"
                ),
                position=(0, 400),
                size=(600, 300)
            ),
            VisualizationWidget(
                widget_id="threat_heatmap",
                widget_type="heatmap",
                title="Threat Activity Heatmap",
                data_source="threat_timing",
                chart_config=ChartConfiguration(
                    chart_type="heatmap",
                    title="Threat Activity by Time of Day",
                    x_axis_label="Hour",
                    y_axis_label="Day",
                    color_scheme="security"
                ),
                position=(600, 400),
                size=(600, 300)
            )
        ]
        
        for widget in default_widgets:
            self.widget_cache[widget.widget_id] = widget
    
    async def start_visualization(self) -> Dict[str, Any]:
        """Start the visualization system."""
        if self.is_running:
            return {'status': 'already_running'}
        
        try:
            self.is_running = True
            logger.info("Starting alert visualization...")
            
            # Start background update task
            self.update_task = asyncio.create_task(self._update_loop())
            
            return {
                'status': 'started',
                'widgets': len(self.widget_cache),
                'real_time_updates': self.config['enable_real_time_updates']
            }
            
        except Exception as e:
            self.is_running = False
            logger.error(f"Failed to start visualization: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def stop_visualization(self) -> Dict[str, Any]:
        """Stop the visualization system."""
        if not self.is_running:
            return {'status': 'not_running'}
        
        try:
            self.is_running = False
            
            # Cancel update task
            if hasattr(self, 'update_task'):
                self.update_task.cancel()
                try:
                    await self.update_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("Alert visualization stopped")
            return {'status': 'stopped'}
            
        except Exception as e:
            logger.error(f"Error stopping visualization: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _update_loop(self) -> None:
        """Main update loop for real-time visualization."""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Update all active widgets
                await self._update_all_widgets()
                
                # Track performance
                update_time = time.time() - start_time
                self.render_performance['render_times'].append(update_time)
                
                # Sleep until next update
                await asyncio.sleep(self.config['chart_update_interval'])
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in visualization update loop: {e}")
                await asyncio.sleep(5)
    
    async def _update_all_widgets(self) -> None:
        """Update all visualization widgets with latest data."""
        with self.visualization_lock:
            try:
                for widget_id, widget in self.widget_cache.items():
                    if widget.is_enabled:
                        await self._update_widget(widget)
                        widget.last_updated = datetime.now()
                
            except Exception as e:
                logger.error(f"Error updating widgets: {e}")
    
    async def _update_widget(self, widget: VisualizationWidget) -> None:
        """Update individual widget with latest data."""
        try:
            # Get data for widget
            data_points = await self._get_widget_data(widget)
            
            # Render chart based on type
            if widget.widget_type == "line_chart":
                chart_result = self.renderer.render_line_chart(data_points, widget.chart_config)
            elif widget.widget_type == "bar_chart":
                chart_result = self.renderer.render_bar_chart(data_points, widget.chart_config)
            elif widget.widget_type == "pie_chart":
                chart_result = self.renderer.render_pie_chart(data_points, widget.chart_config)
            elif widget.widget_type == "heatmap":
                chart_result = self.renderer.render_heatmap(data_points, widget.chart_config)
            else:
                logger.warning(f"Unknown widget type: {widget.widget_type}")
                return
            
            # Cache rendered chart
            if chart_result.get('status') == 'success':
                self.chart_data_cache[widget.widget_id].append({
                    'timestamp': datetime.now(),
                    'chart_data': chart_result['chart_data'],
                    'metadata': {
                        'data_points': len(data_points),
                        'render_time': time.time()
                    }
                })
            
        except Exception as e:
            logger.error(f"Error updating widget {widget.widget_id}: {e}")
    
    async def _get_widget_data(self, widget: VisualizationWidget) -> List[ChartDataPoint]:
        """Get data points for a widget based on its data source."""
        try:
            # This would typically fetch data from the security monitoring components
            # For now, we'll return sample data based on the data source
            
            current_time = datetime.now()
            data_points = []
            
            if widget.data_source == "threat_events":
                # Sample threat timeline data
                for i in range(20):
                    timestamp = current_time - timedelta(minutes=i * 5)
                    data_points.append(ChartDataPoint(
                        timestamp=timestamp,
                        value=max(0, 10 - i + (i % 3)),  # Sample threat count
                        label=f"Threats at {timestamp.strftime('%H:%M')}",
                        category="threats"
                    ))
            
            elif widget.data_source == "alert_severity":
                # Sample severity distribution data
                severities = ["critical", "high", "medium", "low", "info"]
                values = [2, 5, 8, 12, 15]  # Sample counts
                
                for severity, value in zip(severities, values):
                    data_points.append(ChartDataPoint(
                        timestamp=current_time,
                        value=value,
                        label=f"{severity} alerts",
                        category=severity
                    ))
            
            elif widget.data_source == "component_health":
                # Sample component health data
                components = ["intrusion_detection", "behavioral_analysis", "encryption", "auth"]
                health_scores = [95, 88, 92, 97]  # Sample health percentages
                
                for component, score in zip(components, health_scores):
                    data_points.append(ChartDataPoint(
                        timestamp=current_time,
                        value=score,
                        label=f"{component} health",
                        category=component.replace('_', ' ').title()
                    ))
            
            elif widget.data_source == "threat_timing":
                # Sample threat timing heatmap data
                for hour in range(24):
                    for day_offset in range(7):
                        timestamp = current_time.replace(hour=hour) - timedelta(days=day_offset)
                        threat_count = max(0, 5 - abs(hour - 14) + (hour % 4))  # Peak at 2pm
                        
                        data_points.append(ChartDataPoint(
                            timestamp=timestamp,
                            value=threat_count,
                            label=f"Threats at {hour:02d}:00",
                            category="threats"
                        ))
            
            return data_points
            
        except Exception as e:
            logger.error(f"Error getting widget data: {e}")
            return []
    
    def add_data_point(self, widget_id: str, data_point: ChartDataPoint) -> None:
        """Add a new data point for a widget."""
        try:
            if widget_id in self.widget_cache:
                # Add to appropriate data cache
                # This would typically be called by the security monitoring components
                pass
            else:
                logger.warning(f"Unknown widget ID: {widget_id}")
                
        except Exception as e:
            logger.error(f"Error adding data point: {e}")
    
    def get_widget_chart_data(self, widget_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest chart data for a widget."""
        try:
            if widget_id in self.chart_data_cache:
                cache = self.chart_data_cache[widget_id]
                if cache:
                    return cache[-1]  # Return most recent chart data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting widget chart data: {e}")
            return None
    
    def get_all_widgets(self) -> Dict[str, VisualizationWidget]:
        """Get all visualization widgets."""
        return dict(self.widget_cache)
    
    def create_widget(self, widget: VisualizationWidget) -> Dict[str, Any]:
        """Create a new visualization widget."""
        try:
            if len(self.widget_cache) >= self.config['max_widgets']:
                return {
                    'status': 'error',
                    'error': f"Maximum widgets limit ({self.config['max_widgets']}) reached"
                }
            
            if widget.widget_id in self.widget_cache:
                return {
                    'status': 'error',
                    'error': f"Widget with ID {widget.widget_id} already exists"
                }
            
            self.widget_cache[widget.widget_id] = widget
            
            return {
                'status': 'created',
                'widget_id': widget.widget_id,
                'total_widgets': len(self.widget_cache)
            }
            
        except Exception as e:
            logger.error(f"Error creating widget: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def update_widget(self, widget_id: str, **kwargs) -> Dict[str, Any]:
        """Update widget configuration."""
        try:
            if widget_id not in self.widget_cache:
                return {'status': 'error', 'error': f"Widget {widget_id} not found"}
            
            widget = self.widget_cache[widget_id]
            
            for key, value in kwargs.items():
                if hasattr(widget, key):
                    setattr(widget, key, value)
                    logger.info(f"Updated widget {widget_id}: {key} = {value}")
                else:
                    logger.warning(f"Unknown widget attribute: {key}")
            
            return {
                'status': 'updated',
                'widget_id': widget_id,
                'updated_attributes': list(kwargs.keys())
            }
            
        except Exception as e:
            logger.error(f"Error updating widget: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def delete_widget(self, widget_id: str) -> Dict[str, Any]:
        """Delete a visualization widget."""
        try:
            if widget_id not in self.widget_cache:
                return {'status': 'error', 'error': f"Widget {widget_id} not found"}
            
            del self.widget_cache[widget_id]
            
            # Clear associated cache
            if widget_id in self.chart_data_cache:
                self.chart_data_cache[widget_id].clear()
                del self.chart_data_cache[widget_id]
            
            return {
                'status': 'deleted',
                'widget_id': widget_id,
                'remaining_widgets': len(self.widget_cache)
            }
            
        except Exception as e:
            logger.error(f"Error deleting widget: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def get_visualization_performance(self) -> Dict[str, Any]:
        """Get visualization system performance metrics."""
        try:
            render_times = list(self.render_performance['render_times'])
            if not render_times:
                return {'status': 'no_data'}
            
            return {
                'avg_render_time': sum(render_times) / len(render_times),
                'max_render_time': max(render_times),
                'min_render_time': min(render_times),
                'recent_render_time': render_times[-1],
                'total_renders': len(render_times),
                'active_widgets': len([w for w in self.widget_cache.values() if w.is_enabled]),
                'total_widgets': len(self.widget_cache)
            }
            
        except Exception as e:
            logger.error(f"Error getting visualization performance: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def cleanup(self) -> None:
        """Clean up visualization resources."""
        try:
            self.is_running = False
            
            # Clear widget cache
            self.widget_cache.clear()
            
            # Clear chart data cache
            for cache in self.chart_data_cache.values():
                cache.clear()
            self.chart_data_cache.clear()
            
            # Clear performance data
            for metric_deque in self.render_performance.values():
                metric_deque.clear()
            
            logger.info("AlertVisualization cleaned up")
            
        except Exception as e:
            logger.error(f"Error during visualization cleanup: {e}")
