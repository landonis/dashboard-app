# System Info Module

This module provides comprehensive system information for the dashboard application.

## Features

- **Real-time System Monitoring**: CPU usage, memory usage, disk usage, and uptime
- **Process Information**: Running processes with CPU and memory usage
- **Network Information**: Network interfaces and statistics
- **Auto-refresh**: Configurable automatic refresh every 5 seconds
- **Role-based Access**: Admin-only access to system information

## API Endpoints

### GET `/api/modules/system-info`
Returns comprehensive system information including:
- System uptime
- CPU usage percentage
- Memory usage (total, used, free, percentage)
- Disk usage (total, used, free, percentage)
- Load average (1m, 5m, 15m)
- Process count
- Hostname and platform information

### GET `/api/modules/system-info/processes`
Returns top 20 processes sorted by CPU usage:
- Process ID (PID)
- Process name
- CPU percentage
- Memory percentage
- Process status

### GET `/api/modules/system-info/network`
Returns network interface information:
- Interface addresses (IP, netmask, broadcast)
- Interface statistics (status, duplex, speed, MTU)

## Frontend Component

The `SystemInfoPage.tsx` component provides:
- Real-time dashboard with system metrics
- Auto-refresh toggle (5-second intervals)
- Manual refresh button
- Color-coded status indicators (green/yellow/red)
- Progress bars for memory and disk usage
- Responsive design for mobile and desktop

## Dependencies

### Backend
- `psutil` - System and process utilities
- `flask` - Web framework
- `flask-jwt-extended` - JWT authentication

### Frontend
- `react` - UI framework
- `lucide-react` - Icons
- `axios` - HTTP client

## Usage

1. **Access Control**: Only admin users can access system information
2. **Auto-refresh**: Toggle automatic refresh every 5 seconds
3. **Manual Refresh**: Click the refresh button for immediate updates
4. **Visual Indicators**: Color-coded metrics (green < 50%, yellow < 80%, red ≥ 80%)

## Adding New Metrics

To add new system metrics:

1. **Backend**: Add new endpoints to `api.py`
2. **Frontend**: Update `SystemInfoPage.tsx` to display new data
3. **API Service**: Add new API calls to `services/api.ts`

## Security

- JWT authentication required for all endpoints
- Admin role required for access
- Input validation and error handling
- Rate limiting through auto-refresh controls

## Error Handling

- Graceful fallback for unsupported platforms
- Process access denied handling
- Network interface enumeration errors
- User-friendly error messages in UI