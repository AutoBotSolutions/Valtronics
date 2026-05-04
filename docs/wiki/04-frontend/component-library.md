# Component Library Documentation

**Complete guide to Valtronics React component library**

---

## Overview

The Valtronics component library provides a comprehensive set of reusable React components designed specifically for IoT device management and monitoring. The library features a sci-fi themed design system with real-time data visualization capabilities.

---

## Component Architecture

### Component Categories

#### 1. Layout Components
- **Layout**: Main application layout wrapper
- **Header**: Application header with navigation
- **Sidebar**: Navigation sidebar
- **Footer**: Application footer
- **Container**: Responsive container wrapper

#### 2. Data Display Components
- **DeviceCard**: Device information display
- **TelemetryChart**: Real-time data visualization
- **MetricCard**: Key performance indicators
- **AlertPanel**: Alert notification display
- **StatusIndicator**: Status badge/indicator

#### 3. Form Components
- **DeviceForm**: Device creation/editing form
- **AlertForm**: Alert configuration form
- **SearchForm**: Search and filter form
- **SettingsForm**: Configuration settings form

#### 4. Interactive Components
- **DataTable**: Sortable data table
- **FilterPanel**: Advanced filtering interface
- **ActionMenu**: Context menu component
- **Modal**: Modal dialog wrapper
- **Tooltip**: Tooltip component

#### 5. Visualization Components
- **LineChart**: Time series line chart
- **BarChart**: Bar chart component
- **PieChart**: Pie chart component
- **GaugeChart**: Gauge/meter chart
- **Heatmap**: Data heatmap visualization

---

## Installation and Setup

### Installation
```bash
# Install component library dependencies
npm install @valtronics/components
npm install @mui/material @emotion/react @emotion/styled
npm install @mui/icons-material @mui/lab
npm install recharts react-chartjs-2 chart.js
```

### Theme Configuration
```typescript
// src/theme/index.ts
import { createTheme } from '@mui/material/styles';

export const valtronicsTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00ffff', // Cyan
      light: '#40ffff',
      dark: '#00cccc',
    },
    secondary: {
      main: '#ff00ff', // Magenta
      light: '#ff40ff',
      dark: '#cc00cc',
    },
    accent: {
      main: '#ffd700', // Gold
      light: '#ffed4e',
      dark: '#c9a700',
    },
    background: {
      default: '#0a0a0f', // Dark background
      paper: '#1a1a2e',
    },
    text: {
      primary: '#ffffff',
      secondary: '#b8b8c8',
    },
  },
  typography: {
    fontFamily: '"Orbitron", "Space Mono", monospace',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
      color: '#00ffff',
      textShadow: '0 0 10px rgba(0, 255, 255, 0.5)',
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
      color: '#ffd700',
    },
    body1: {
      fontSize: '1rem',
      color: '#ffffff',
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
          border: '1px solid #00ffff',
          boxShadow: '0 0 20px rgba(0, 255, 255, 0.3)',
          borderRadius: '12px',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(135deg, #00ffff 0%, #00cccc 100%)',
          color: '#0a0a0f',
          fontWeight: 'bold',
          textTransform: 'none',
          '&:hover': {
            background: 'linear-gradient(135deg, #40ffff 0%, #00ffff 100%)',
            boxShadow: '0 0 30px rgba(0, 255, 255, 0.5)',
          },
        },
      },
    },
  },
});
```

---

## Core Components

### Layout Component

#### Layout
```typescript
// src/components/Layout/Layout.tsx
import React from 'react';
import { Box, CssBaseline } from '@mui/material';
import { Header } from '../Header/Header';
import { Sidebar } from '../Sidebar/Sidebar';
import { Footer } from '../Footer/Footer';

interface LayoutProps {
  children: React.ReactNode;
  sidebarOpen?: boolean;
  onSidebarToggle?: () => void;
}

export const Layout: React.FC<LayoutProps> = ({
  children,
  sidebarOpen = true,
  onSidebarToggle,
}) => {
  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <CssBaseline />
      
      {/* Header */}
      <Header 
        onSidebarToggle={onSidebarToggle}
        sidebarOpen={sidebarOpen}
      />
      
      {/* Sidebar */}
      <Sidebar open={sidebarOpen} />
      
      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          pt: 8, // Header height
          pl: sidebarOpen ? 30 : 8, // Account for sidebar
          transition: 'padding-left 0.3s ease',
        }}
      >
        {children}
      </Box>
      
      {/* Footer */}
      <Footer />
    </Box>
  );
};
```

#### Header
```typescript
// src/components/Header/Header.tsx
import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  Badge,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';

interface HeaderProps {
  onSidebarToggle?: () => void;
  sidebarOpen?: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  onSidebarToggle,
  sidebarOpen,
}) => {
  return (
    <AppBar
      position="fixed"
      sx={{
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
        borderBottom: '2px solid #00ffff',
        boxShadow: '0 4px 20px rgba(0, 255, 255, 0.3)',
        zIndex: (theme) => theme.zIndex.drawer + 1,
      }}
    >
      <Toolbar>
        {/* Menu Button */}
        <IconButton
          color="inherit"
          edge="start"
          onClick={onSidebarToggle}
          sx={{ mr: 2 }}
        >
          <MenuIcon sx={{ color: '#00ffff' }} />
        </IconButton>

        {/* Logo and Title */}
        <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center' }}>
          <Typography
            variant="h6"
            component="div"
            sx={{
              fontFamily: '"Orbitron", monospace',
              color: '#ffd700',
              textShadow: '0 0 10px rgba(255, 215, 0, 0.5)',
            }}
          >
            VALTRONICS
          </Typography>
        </Box>

        {/* Right Side Actions */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {/* Notifications */}
          <IconButton color="inherit">
            <Badge badgeContent={3} color="error">
              <NotificationsIcon sx={{ color: '#00ffff' }} />
            </Badge>
          </IconButton>

          {/* Settings */}
          <IconButton color="inherit">
            <SettingsIcon sx={{ color: '#00ffff' }} />
          </IconButton>
        </Box>
      </Toolbar>
    </AppBar>
  );
};
```

### Data Display Components

#### DeviceCard
```typescript
// src/components/DeviceCard/DeviceCard.tsx
import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Chip,
  Box,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  PowerSettingsNew as PowerIcon,
} from '@mui/icons-material';
import { Device, DeviceStatus } from '../../types/device';
import { getStatusColor, getStatusIcon } from '../../utils/deviceUtils';

interface DeviceCardProps {
  device: Device;
  onEdit?: (device: Device) => void;
  onDelete?: (deviceId: number) => void;
  onTogglePower?: (deviceId: number) => void;
}

export const DeviceCard: React.FC<DeviceCardProps> = ({
  device,
  onEdit,
  onDelete,
  onTogglePower,
}) => {
  const statusColor = getStatusColor(device.status);
  const StatusIcon = getStatusIcon(device.status);

  return (
    <Card
      sx={{
        height: '100%',
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
        border: `1px solid ${statusColor}`,
        boxShadow: `0 0 20px ${statusColor}40`,
        borderRadius: '12px',
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: `0 8px 30px ${statusColor}60`,
        },
      }}
    >
      <CardContent>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography
            variant="h6"
            component="h3"
            sx={{
              color: '#00ffff',
              fontFamily: '"Orbitron", monospace',
              textShadow: '0 0 5px rgba(0, 255, 255, 0.5)',
            }}
          >
            {device.name}
          </Typography>
          
          <Chip
            icon={<StatusIcon />}
            label={device.status}
            size="small"
            sx={{
              backgroundColor: statusColor,
              color: '#ffffff',
              fontWeight: 'bold',
            }}
          />
        </Box>

        {/* Device Information */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" sx={{ color: '#b8b8c8', mb: 1 }}>
            <strong>ID:</strong> {device.deviceId}
          </Typography>
          <Typography variant="body2" sx={{ color: '#b8b8c8', mb: 1 }}>
            <strong>Type:</strong> {device.deviceType}
          </Typography>
          {device.location && (
            <Typography variant="body2" sx={{ color: '#b8b8c8', mb: 1 }}>
              <strong>Location:</strong> {device.location}
            </Typography>
          )}
          {device.lastSeen && (
            <Typography variant="body2" sx={{ color: '#b8b8c8' }}>
              <strong>Last Seen:</strong> {new Date(device.lastSeen).toLocaleString()}
            </Typography>
          )}
        </Box>

        {/* Action Buttons */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
          <Box>
            {onEdit && (
              <Tooltip title="Edit Device">
                <IconButton
                  size="small"
                  onClick={() => onEdit(device)}
                  sx={{ color: '#00ffff' }}
                >
                  <EditIcon />
                </IconButton>
              </Tooltip>
            )}
            
            {onDelete && (
              <Tooltip title="Delete Device">
                <IconButton
                  size="small"
                  onClick={() => onDelete(device.id)}
                  sx={{ color: '#ff4444' }}
                >
                  <DeleteIcon />
                </IconButton>
              </Tooltip>
            )}
          </Box>

          {onTogglePower && (
            <Tooltip title={device.isActive ? 'Deactivate' : 'Activate'}>
              <IconButton
                size="small"
                onClick={() => onTogglePower(device.id)}
                sx={{
                  color: device.isActive ? '#00ff00' : '#ff4444',
                }}
              >
                <PowerIcon />
              </IconButton>
            </Tooltip>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};
```

#### TelemetryChart
```typescript
// src/components/TelemetryChart/TelemetryChart.tsx
import React, { useEffect, useRef } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions,
} from 'chart.js';
import { TelemetryData } from '../../types/telemetry';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface TelemetryChartProps {
  data: TelemetryData[];
  title?: string;
  height?: number;
  showControls?: boolean;
}

export const TelemetryChart: React.FC<TelemetryChartProps> = ({
  data,
  title = 'Telemetry Data',
  height = 300,
  showControls = true,
}) => {
  const [selectedMetric, setSelectedMetric] = React.useState<string>('temperature');
  const chartRef = useRef<ChartJS<'line'>>(null);

  // Prepare chart data
  const chartData = React.useMemo(() => {
    const timestamps = data.map(d => 
      new Date(d.timestamp).toLocaleTimeString()
    );
    
    const datasets = Object.keys(data[0]?.metrics || {}).map(metric => ({
      label: metric.charAt(0).toUpperCase() + metric.slice(1),
      data: data.map(d => d.metrics[metric]?.value || 0),
      borderColor: getMetricColor(metric),
      backgroundColor: `${getMetricColor(metric)}20`,
      borderWidth: 2,
      tension: 0.4,
      pointRadius: 3,
      pointHoverRadius: 6,
      hidden: metric !== selectedMetric,
    }));

    return {
      labels: timestamps,
      datasets,
    };
  }, [data, selectedMetric]);

  // Chart options
  const options: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#ffffff',
          font: {
            family: '"Orbitron", monospace',
          },
        },
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#00ffff',
        bodyColor: '#ffffff',
        borderColor: '#00ffff',
        borderWidth: 1,
      },
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        ticks: {
          color: '#b8b8c8',
        },
      },
      y: {
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        ticks: {
          color: '#b8b8c8',
        },
      },
    },
  };

  const getMetricColor = (metric: string): string => {
    const colors: Record<string, string> = {
      temperature: '#ff6b6b',
      humidity: '#4ecdc4',
      pressure: '#45b7d1',
      voltage: '#96ceb4',
      current: '#feca57',
    };
    return colors[metric] || '#00ffff';
  };

  const handleMetricChange = (event: any) => {
    setSelectedMetric(event.target.value);
  };

  useEffect(() => {
    if (chartRef.current) {
      chartRef.current.update();
    }
  }, [data]);

  return (
    <Card
      sx={{
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
        border: '1px solid #00ffff',
        boxShadow: '0 0 20px rgba(0, 255, 255, 0.3)',
        borderRadius: '12px',
      }}
    >
      <CardContent>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography
            variant="h6"
            sx={{
              color: '#ffd700',
              fontFamily: '"Orbitron", monospace',
              textShadow: '0 0 5px rgba(255, 215, 0, 0.5)',
            }}
          >
            {title}
          </Typography>

          {showControls && (
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel sx={{ color: '#b8b8c8' }}>Metric</InputLabel>
              <Select
                value={selectedMetric}
                onChange={handleMetricChange}
                label="Metric"
                sx={{
                  color: '#ffffff',
                  '& .MuiOutlinedInput-notchedOutline': {
                    borderColor: '#00ffff',
                  },
                  '&:hover .MuiOutlinedInput-notchedOutline': {
                    borderColor: '#40ffff',
                  },
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                    borderColor: '#ffd700',
                  },
                }}
              >
                {Object.keys(data[0]?.metrics || {}).map(metric => (
                  <MenuItem key={metric} value={metric}>
                    {metric.charAt(0).toUpperCase() + metric.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          )}
        </Box>

        {/* Chart */}
        <Box sx={{ height, position: 'relative' }}>
          <Line ref={chartRef} data={chartData} options={options} />
        </Box>
      </CardContent>
    </Card>
  );
};
```

#### MetricCard
```typescript
// src/components/MetricCard/MetricCard.tsx
import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  TrendingUp,
  TrendingDown,
  TrendingFlat,
} from '@mui/icons-material';
import { MetricData } from '../../types/metrics';

interface MetricCardProps {
  metric: MetricData;
  showTrend?: boolean;
  height?: number;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  metric,
  showTrend = true,
  height = 120,
}) => {
  const getTrendIcon = (trend: 'up' | 'down' | 'stable') => {
    const iconProps = {
      fontSize: 'small' as const,
      sx: { ml: 1 },
    };

    switch (trend) {
      case 'up':
        return <TrendingUp {...iconProps} sx={{ ...iconProps.sx, color: '#00ff00' }} />;
      case 'down':
        return <TrendingDown {...iconProps} sx={{ ...iconProps.sx, color: '#ff4444' }} />;
      case 'stable':
        return <TrendingFlat {...iconProps} sx={{ ...iconProps.sx, color: '#ffd700' }} />;
    }
  };

  const getValueColor = (value: number, threshold?: number) => {
    if (!threshold) return '#00ffff';
    
    if (value > threshold * 1.2) return '#ff4444';
    if (value > threshold) return '#ffd700';
    return '#00ff00';
  };

  return (
    <Card
      sx={{
        height,
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
        border: '1px solid #00ffff',
        boxShadow: '0 0 20px rgba(0, 255, 255, 0.3)',
        borderRadius: '12px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
      }}
    >
      <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        {/* Title */}
        <Typography
          variant="body2"
          sx={{
            color: '#b8b8c8',
            mb: 1,
            fontFamily: '"Space Mono", monospace',
          }}
        >
          {metric.name}
        </Typography>

        {/* Value */}
        <Box sx={{ display: 'flex', alignItems: 'baseline', mb: 1 }}>
          <Typography
            variant="h4"
            component="div"
            sx={{
              color: getValueColor(metric.value, metric.threshold),
              fontFamily: '"Orbitron", monospace',
              fontWeight: 'bold',
              textShadow: `0 0 10px ${getValueColor(metric.value, metric.threshold)}40`,
            }}
          >
            {metric.value}
          </Typography>
          <Typography
            variant="body2"
            sx={{
              color: '#b8b8c8',
              ml: 1,
              fontFamily: '"Space Mono", monospace',
            }}
          >
            {metric.unit}
          </Typography>
        </Box>

        {/* Trend */}
        {showTrend && metric.trend && (
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Typography
              variant="body2"
              sx={{
                color: '#b8b8c8',
                fontFamily: '"Space Mono", monospace',
              }}
            >
              {metric.trend === 'up' && '+'}
              {metric.change}%
            </Typography>
            {getTrendIcon(metric.trend)}
          </Box>
        )}
      </CardContent>
    </Card>
  );
};
```

### Form Components

#### DeviceForm
```typescript
// src/components/DeviceForm/DeviceForm.tsx
import React from 'react';
import {
  Box,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Grid,
  Typography,
} from '@mui/material';
import { Device, DeviceCreate, DeviceType } from '../../types/device';

interface DeviceFormProps {
  device?: Device;
  onSubmit: (data: DeviceCreate) => void;
  onCancel: () => void;
  loading?: boolean;
}

export const DeviceForm: React.FC<DeviceFormProps> = ({
  device,
  onSubmit,
  onCancel,
  loading = false,
}) => {
  const [formData, setFormData] = React.useState<DeviceCreate>({
    name: device?.name || '',
    deviceId: device?.deviceId || '',
    deviceType: device?.deviceType || DeviceType.SENSOR,
    manufacturer: device?.manufacturer || '',
    model: device?.model || '',
    firmwareVersion: device?.firmwareVersion || '',
    location: device?.location || '',
  });

  const handleChange = (field: keyof DeviceCreate) => (
    event: React.ChangeEvent<HTMLInputElement | { value: string }>
  ) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value,
    }));
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    onSubmit(formData);
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
      <Typography
        variant="h6"
        sx={{
          color: '#ffd700',
          mb: 3,
          fontFamily: '"Orbitron", monospace',
          textShadow: '0 0 5px rgba(255, 215, 0, 0.5)',
        }}
      >
        {device ? 'Edit Device' : 'Create Device'}
      </Typography>

      <Grid container spacing={3}>
        {/* Device Name */}
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Device Name"
            value={formData.name}
            onChange={handleChange('name')}
            required
            sx={{
              '& .MuiInputLabel-root': { color: '#b8b8c8' },
              '& .MuiOutlinedInput-root': {
                '& fieldset': { borderColor: '#00ffff' },
                '&:hover fieldset': { borderColor: '#40ffff' },
                '&.Mui-focused fieldset': { borderColor: '#ffd700' },
              },
              '& .MuiInputBase-input': { color: '#ffffff' },
            }}
          />
        </Grid>

        {/* Device ID */}
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Device ID"
            value={formData.deviceId}
            onChange={handleChange('deviceId')}
            required
            disabled={!!device}
            sx={{
              '& .MuiInputLabel-root': { color: '#b8b8c8' },
              '& .MuiOutlinedInput-root': {
                '& fieldset': { borderColor: '#00ffff' },
                '&:hover fieldset': { borderColor: '#40ffff' },
                '&.Mui-focused fieldset': { borderColor: '#ffd700' },
              },
              '& .MuiInputBase-input': { color: '#ffffff' },
            }}
          />
        </Grid>

        {/* Device Type */}
        <Grid item xs={12} sm={6}>
          <FormControl fullWidth required>
            <InputLabel sx={{ color: '#b8b8c8' }}>Device Type</InputLabel>
            <Select
              value={formData.deviceType}
              onChange={handleChange('deviceType')}
              label="Device Type"
              sx={{
                color: '#ffffff',
                '& .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#00ffff',
                },
                '&:hover .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#40ffff',
                },
                '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#ffd700',
                },
              }}
            >
              {Object.values(DeviceType).map(type => (
                <MenuItem key={type} value={type}>
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        {/* Manufacturer */}
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Manufacturer"
            value={formData.manufacturer}
            onChange={handleChange('manufacturer')}
            sx={{
              '& .MuiInputLabel-root': { color: '#b8b8c8' },
              '& .MuiOutlinedInput-root': {
                '& fieldset': { borderColor: '#00ffff' },
                '&:hover fieldset': { borderColor: '#40ffff' },
                '&.Mui-focused fieldset': { borderColor: '#ffd700' },
              },
              '& .MuiInputBase-input': { color: '#ffffff' },
            }}
          />
        </Grid>

        {/* Model */}
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Model"
            value={formData.model}
            onChange={handleChange('model')}
            sx={{
              '& .MuiInputLabel-root': { color: '#b8b8c8' },
              '& .MuiOutlinedInput-root': {
                '& fieldset': { borderColor: '#00ffff' },
                '&:hover fieldset': { borderColor: '#40ffff' },
                '&.Mui-focused fieldset': { borderColor: '#ffd700' },
              },
              '& .MuiInputBase-input': { color: '#ffffff' },
            }}
          />
        </Grid>

        {/* Firmware Version */}
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Firmware Version"
            value={formData.firmwareVersion}
            onChange={handleChange('firmwareVersion')}
            sx={{
              '& .MuiInputLabel-root': { color: '#b8b8c8' },
              '& .MuiOutlinedInput-root': {
                '& fieldset': { borderColor: '#00ffff' },
                '&:hover fieldset': { borderColor: '#40ffff' },
                '&.Mui-focused fieldset': { borderColor: '#ffd700' },
              },
              '& .MuiInputBase-input': { color: '#ffffff' },
            }}
          />
        </Grid>

        {/* Location */}
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Location"
            value={formData.location}
            onChange={handleChange('location')}
            sx={{
              '& .MuiInputLabel-root': { color: '#b8b8c8' },
              '& .MuiOutlinedInput-root': {
                '& fieldset': { borderColor: '#00ffff' },
                '&:hover fieldset': { borderColor: '#40ffff' },
                '&.Mui-focused fieldset': { borderColor: '#ffd700' },
              },
              '& .MuiInputBase-input': { color: '#ffffff' },
            }}
          />
        </Grid>

        {/* Action Buttons */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
            <Button
              onClick={onCancel}
              variant="outlined"
              sx={{
                borderColor: '#ff4444',
                color: '#ff4444',
                '&:hover': {
                  borderColor: '#ff6666',
                  backgroundColor: 'rgba(255, 68, 68, 0.1)',
                },
              }}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="contained"
              disabled={loading}
              sx={{
                background: 'linear-gradient(135deg, #00ffff 0%, #00cccc 100%)',
                color: '#0a0a0f',
                fontWeight: 'bold',
                '&:hover': {
                  background: 'linear-gradient(135deg, #40ffff 0%, #00ffff 100%)',
                  boxShadow: '0 0 30px rgba(0, 255, 255, 0.5)',
                },
                '&:disabled': {
                  background: 'gray',
                  color: '#666',
                },
              }}
            >
              {device ? 'Update' : 'Create'}
            </Button>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};
```

---

## Usage Examples

### Basic Usage
```typescript
// App.tsx
import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { Layout } from '@valtronics/components/Layout';
import { DeviceCard } from '@valtronics/components/DeviceCard';
import { TelemetryChart } from '@valtronics/components/TelemetryChart';
import { MetricCard } from '@valtronics/components/MetricCard';

const theme = createTheme({
  // Your custom theme configuration
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Layout>
        <DeviceCard
          device={device}
          onEdit={handleEdit}
          onDelete={handleDelete}
        />
        <TelemetryChart
          data={telemetryData}
          title="Temperature Trends"
          height={400}
        />
        <MetricCard
          metric={temperatureMetric}
          showTrend
        />
      </Layout>
    </ThemeProvider>
  );
}
```

### Advanced Usage with Custom Styling
```typescript
// CustomDashboard.tsx
import React from 'react';
import { Box, Grid } from '@mui/material';
import { DeviceCard } from '@valtronics/components/DeviceCard';
import { TelemetryChart } from '@valtronics/components/TelemetryChart';

export const CustomDashboard: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6} lg={4}>
          <DeviceCard
            device={device}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        </Grid>
        <Grid item xs={12} md={12} lg={8}>
          <TelemetryChart
            data={telemetryData}
            title="Real-time Telemetry"
            height={400}
            showControls
          />
        </Grid>
      </Grid>
    </Box>
  );
};
```

---

## Customization

### Theme Customization
```typescript
// customTheme.ts
import { createTheme } from '@mui/material/styles';

export const customTheme = createTheme({
  palette: {
    primary: {
      main: '#your-primary-color',
    },
    // Override other theme properties
  },
  components: {
    // Override component styles
    DeviceCard: {
      styleOverrides: {
        root: {
          // Custom styles for DeviceCard
        },
      },
    },
  },
});
```

### Component Props
All components accept standard props plus custom props for specific functionality:

#### DeviceCard Props
- `device`: Device object
- `onEdit`: Edit callback function
- `onDelete`: Delete callback function
- `onTogglePower`: Power toggle callback function
- `showActions`: Boolean to show/hide action buttons

#### TelemetryChart Props
- `data`: Telemetry data array
- `title`: Chart title
- `height`: Chart height in pixels
- `showControls`: Boolean to show metric selection controls
- `onMetricChange`: Metric change callback function

#### MetricCard Props
- `metric`: Metric data object
- `showTrend`: Boolean to show/hide trend indicator
- `height`: Card height in pixels
- `onClick`: Click callback function

---

## Best Practices

### Performance
- Use React.memo for expensive components
- Implement proper key props for lists
- Use useCallback for event handlers
- Optimize re-renders with useMemo

### Accessibility
- Use semantic HTML elements
- Implement proper ARIA labels
- Ensure keyboard navigation
- Test with screen readers

### Testing
- Write unit tests for all components
- Test component interactions
- Mock external dependencies
- Use React Testing Library

### Code Organization
- Keep components focused and single-purpose
- Use proper TypeScript types
- Follow consistent naming conventions
- Document component APIs

---

## Support

For component library support:
- **Documentation**: [Frontend Overview](frontend-overview.md)
- **Development**: [Development Setup](../08-development/development-setup.md)
- **Contributing**: [Contributing Guidelines](../08-development/contributing.md)
- **Troubleshooting**: [Troubleshooting Guide](../10-reference/troubleshooting.md)
- **Email**: autobotsolution@gmail.com

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**Component Library Documentation v1.0**
