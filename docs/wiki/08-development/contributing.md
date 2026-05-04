# Contributing Guidelines

**Guide for contributing to the Valtronics project**

---

## Overview

Thank you for your interest in contributing to Valtronics! This guide provides comprehensive information on how to contribute to the project, including development workflows, coding standards, and best practices.

---

## Getting Started

### Prerequisites
- Read the [Development Setup Guide](development-setup.md)
- Set up your local development environment
- Familiarize yourself with the project structure
- Review existing code and documentation

### Contributor Agreement
By contributing to Valtronics, you agree to:
- Respect the project's code of conduct
- Follow the established development workflows
- Maintain high code quality standards
- Provide appropriate documentation for changes

---

## Development Workflow

### 1. Fork and Clone
```bash
# Fork the repository on GitHub
git clone https://github.com/YOUR_USERNAME/valtronics.git
cd valtronics

# Add upstream remote
git remote add upstream https://github.com/valtronics/valtronics.git
```

### 2. Create Feature Branch
```bash
# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name
```

### 3. Make Changes
- Follow the coding standards outlined below
- Write tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 4. Commit Changes
```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: Add new device management feature

- Implement device CRUD operations
- Add comprehensive test coverage
- Update API documentation

Fixes #123"
```

### 5. Push and Create Pull Request
```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
```

### 6. Code Review
- Wait for code review feedback
- Address any issues raised
- Update your branch as needed
- Request review when ready

### 7. Merge
- Once approved, maintainers will merge your PR
- Delete your feature branch
- Sync with upstream main

---

## Coding Standards

### Python (Backend)

#### Code Style
Follow PEP 8 and use the following tools:
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

#### Code Formatting
```python
# Use Black formatting
black app/

# Use isort for imports
isort app/

# Check for issues
flake8 app/
mypy app/
```

#### Type Hints
```python
from typing import List, Dict, Optional, Union
from pydantic import BaseModel

class Device(BaseModel):
    """Device model with type hints."""
    
    id: int
    name: str
    device_id: str
    device_type: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    firmware_version: Optional[str] = None
    location: Optional[str] = None
    status: str = "offline"
    is_active: bool = True
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
```

#### Documentation Strings
```python
def create_device(device: DeviceCreate, db: Session) -> Device:
    """
    Create a new device in the database.
    
    Args:
        device: Device creation data
        db: Database session
        
    Returns:
        Created device object
        
    Raises:
        ValueError: If device_id already exists
        DatabaseError: If database operation fails
        
    Example:
        >>> device_data = DeviceCreate(name="Test Device", device_id="TEST-001")
        >>> device = create_device(device_data, db)
        >>> print(device.name)
        "Test Device"
    """
    # Implementation here
    pass
```

#### Error Handling
```python
from app.core.exceptions import ValidationError, DatabaseError

def get_device(device_id: int, db: Session) -> Device:
    """
    Get device by ID with proper error handling.
    """
    try:
        device = db.query(Device).filter(Device.id == device_id).first()
        if not device:
            raise ValidationError(f"Device with id {device_id} not found")
        return device
    except DatabaseError as e:
        logger.error(f"Database error getting device {device_id}: {e}")
        raise DatabaseError(f"Failed to retrieve device {device_id}") from e
```

### JavaScript/TypeScript (Frontend)

#### Code Style
- Use ESLint with TypeScript rules
- Use Prettier for formatting
- Follow React best practices
- Use functional components with hooks

#### Component Structure
```typescript
// src/components/DeviceCard.tsx
import React, { useState, useEffect } from 'react';
import { Device, DeviceStatus } from '../types/device';
import { deviceService } from '../services/deviceService';
import { formatDateTime } from '../utils/dateUtils';

interface DeviceCardProps {
  device: Device;
  onUpdate: (device: Device) => void;
  onDelete: (deviceId: number) => void;
}

export const DeviceCard: React.FC<DeviceCardProps> = ({ 
  device, 
  onUpdate, 
  onDelete 
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Component logic here
  }, [device]);

  const handleUpdate = async (updates: Partial<Device>) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const updatedDevice = await deviceService.updateDevice(device.id, updates);
      onUpdate(updatedDevice);
    } catch (err) {
      setError('Failed to update device');
      console.error('Update error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this device?')) {
      return;
    }

    try {
      await deviceService.deleteDevice(device.id);
      onDelete(device.id);
    } catch (err) {
      setError('Failed to delete device');
      console.error('Delete error:', err);
    }
  };

  return (
    <div className="device-card">
      {/* Component JSX here */}
    </div>
  );
};
```

#### TypeScript Types
```typescript
// src/types/device.ts
export interface Device {
  id: number;
  name: string;
  deviceId: string;
  deviceType: string;
  manufacturer?: string;
  model?: string;
  firmwareVersion?: string;
  location?: string;
  status: DeviceStatus;
  isActive: boolean;
  metadata: Record<string, any>;
  createdAt: string;
  updatedAt: string;
  lastSeen?: string;
}

export enum DeviceStatus {
  ONLINE = 'online',
  OFFLINE = 'offline',
  WARNING = 'warning',
  ERROR = 'error',
  MAINTENANCE = 'maintenance'
}

export interface DeviceCreate {
  name: string;
  deviceId: string;
  deviceType: string;
  manufacturer?: string;
  model?: string;
  firmwareVersion?: string;
  location?: string;
}
```

---

## Testing Standards

### Backend Testing

#### Unit Tests
```python
# tests/unit/test_device_service.py
import pytest
from unittest.mock import Mock, patch
from app.services.device_service import DeviceService
from app.models.device import Device
from app.schemas.device import DeviceCreate

class TestDeviceService:
    def setup_method(self):
        self.device_service = DeviceService()
        self.mock_db = Mock()
    
    def test_create_device_success(self):
        """Test successful device creation."""
        device_data = DeviceCreate(
            name="Test Device",
            device_id="TEST-001",
            device_type="sensor"
        )
        
        expected_device = Device(
            id=1,
            name="Test Device",
            device_id="TEST-001",
            device_type="sensor",
            status="offline"
        )
        
        with patch.object(self.device_service, 'db', self.mock_db):
            self.mock_db.query.return_value.filter.return_value.first.return_value = None
            self.mock_db.add.return_value = expected_device
            self.mock_db.commit.return_value = None
            self.mock_db.refresh.return_value = expected_device
            
            result = self.device_service.create_device(device_data, self.mock_db)
            
            assert result.name == "Test Device"
            assert result.device_id == "TEST-001"
            assert result.device_type == "sensor"
            assert result.status == "offline"
    
    def test_create_device_duplicate_id(self):
        """Test device creation with duplicate ID."""
        device_data = DeviceCreate(
            name="Test Device",
            device_id="TEST-001",
            device_type="sensor"
        )
        
        with patch.object(self.device_service, 'db', self.mock_db):
            self.mock_db.query.return_value.filter.return_value.first.return_value = Device(
                id=1,
                device_id="TEST-001"
            )
            
            with pytest.raises(ValidationError, match="Device ID already exists"):
                self.device_service.create_device(device_data, self.mock_db)
```

#### Integration Tests
```python
# tests/integration/test_api.py
import pytest
from httpx import AsyncClient
from app.main_sqlite import app
from app.db.session_sqlite import get_db

@pytest.mark.asyncio
async def test_create_device_api():
    """Test device creation API endpoint."""
    async with AsyncClient(app=app) as client:
        device_data = {
            "name": "Test Device",
            "device_id": "TEST-001",
            "device_type": "sensor"
        }
        
        response = await client.post("/api/v1/devices/", json=device_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Test Device"
        assert data["data"]["device_id"] == "TEST-001"
```

### Frontend Testing

#### Component Tests
```typescript
// src/components/__tests__/DeviceCard.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { DeviceCard } from '../DeviceCard';
import { Device, DeviceStatus } from '../../types/device';
import { deviceService } from '../../services/deviceService';

// Mock the service
jest.mock('../../services/deviceService');
const mockDeviceService = deviceService as jest.Mocked<typeof deviceService>;

describe('DeviceCard', () => {
  const mockDevice: Device = {
    id: 1,
    name: 'Test Device',
    deviceId: 'TEST-001',
    deviceType: 'sensor',
    status: DeviceStatus.ONLINE,
    isActive: true,
    metadata: {},
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z'
  };

  const mockOnUpdate = jest.fn();
  const mockOnDelete = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders device information correctly', () => {
    render(
      <DeviceCard 
        device={mockDevice} 
        onUpdate={mockOnUpdate} 
        onDelete={mockOnDelete} 
      />
    );

    expect(screen.getByText('Test Device')).toBeInTheDocument();
    expect(screen.getByText('TEST-001')).toBeInTheDocument();
    expect(screen.getByText('sensor')).toBeInTheDocument();
    expect(screen.getByText('online')).toBeInTheDocument();
  });

  it('calls onUpdate when update button is clicked', async () => {
    render(
      <DeviceCard 
        device={mockDevice} 
        onUpdate={mockOnUpdate} 
        onDelete={mockOnDelete} 
      />
    );

    const updateButton = screen.getByRole('button', { name: 'Update' });
    fireEvent.click(updateButton);

    await waitFor(() => {
      expect(mockOnUpdate).toHaveBeenCalledWith(mockDevice);
    });
  });

  it('shows confirmation dialog when delete button is clicked', () => {
    // Mock window.confirm
    const originalConfirm = window.confirm;
    window.confirm = jest.fn(() => true);

    render(
      <DeviceCard 
        device={mockDevice} 
        onUpdate={mockOnUpdate} 
        onDelete={mockOnDelete} 
      />
    );

    const deleteButton = screen.getByRole('button', { name: 'Delete' });
    fireEvent.click(deleteButton);

    expect(window.confirm).toHaveBeenCalledWith(
      'Are you sure you want to delete this device?'
    );

    // Restore original confirm
    window.confirm = originalConfirm;
  });
});
```

---

## Documentation Standards

### API Documentation
- Use OpenAPI/Swagger annotations
- Provide clear parameter descriptions
- Include example requests and responses
- Document error codes and messages

```python
@router.post("/devices/", response_model=DeviceResponse, status_code=201)
async def create_device(
    device: DeviceCreate,
    db: Session = Depends(get_db)
) -> DeviceResponse:
    """
    Create a new device in the system.
    
    Args:
        device: Device creation data
        db: Database session
        
    Returns:
        Created device information
        
    Raises:
        ValidationError: If device ID already exists
        DatabaseError: If database operation fails
        
    Example:
        >>> device_data = DeviceCreate(name="Test Device", device_id="TEST-001")
        >>> response = client.post("/api/v1/devices/", json=device_data.json())
        >>> response.status_code
        201
    """
```

### Code Comments
- Add docstrings to all functions and classes
- Comment complex logic
- Use TODO and FIXME markers appropriately
- Include type hints for better documentation

```python
def calculate_device_health(device: Device, telemetry_data: List[TelemetryData]) -> float:
    """
    Calculate health score for a device based on telemetry data.
    
    Args:
        device: Device object
        telemetry_data: List of recent telemetry data points
        
    Returns:
        Health score between 0.0 and 1.0
        
    Note:
        Health score calculation considers:
        - Data completeness (40% weight)
        - Data accuracy (30% weight)
        - Response time (20% weight)
        - Error rate (10% weight)
    """
    # Implementation here
    pass
```

### README Updates
- Update README.md for major features
- Document breaking changes
- Update API documentation
- Add migration guides when needed

---

## Pull Request Guidelines

### PR Requirements
- **Title**: Clear, descriptive title
- **Description**: Detailed description of changes
- **Tests**: All tests must pass
- **Documentation**: Updated as needed
- **Code Quality**: Must pass all linting checks

### PR Template
```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review of the code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes (or documented)
```

### Review Process
1. **Automated Checks**: CI/CD pipeline checks
2. **Code Review**: At least one maintainer review
3. **Testing**: Automated and manual testing
4. **Documentation**: Documentation review
5. **Approval**: Maintainer approval required

---

## Code Review Guidelines

### Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests are comprehensive
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] No performance regressions
- [ ] Error handling is appropriate
- [ ] No breaking changes (or documented)

### Review Comments
- Be constructive and specific
- Provide suggestions for improvement
- Explain reasoning for changes
- Ask questions if something is unclear
- Be respectful and professional

### Review Response Guidelines
- Address all reviewer comments
- Explain decisions made
- Update code as needed
- Ask for clarification if needed
- Be responsive and timely

---

## Release Process

### Version Bumping
- **Patch**: `x.y.z+1` (bug fixes)
- **Minor**: `x.y+1.0` (new features, backward compatible)
- **Major**: `x+1.0.0` (breaking changes)

### Release Checklist
- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version numbers updated
- [ ] Tagged in Git
- [ ] Release notes prepared

---

## Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Welcome new contributors
- Provide helpful guidance
- Focus on what is best for the community
- Show empathy towards other community members

### Communication
- Use clear and professional language
- Be patient with newcomers
- Provide constructive feedback
- Ask questions if unsure
- Share knowledge and help others

### Issue Reporting
- Use GitHub issues for bug reports
- Provide detailed information
- Include reproduction steps
- Use appropriate labels
- Be responsive to maintainer questions

---

## Development Tools

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

### IDE Configuration
- Use provided VS Code settings
- Configure linting and formatting tools
- Set up debugging configurations
- Use recommended extensions

### Continuous Integration
- Automated testing on PRs
- Code quality checks
- Security scanning
- Performance testing

---

## Troubleshooting

### Common Issues

#### Development Setup
- Python version compatibility
- Node.js version conflicts
- Database connection issues
- Port conflicts

#### Testing
- Test environment setup
- Mock configuration
- Test data management
- Coverage reporting

#### Code Quality
- Linting errors
- Type checking issues
- Code formatting problems
- Documentation gaps

### Getting Help
- Check existing issues and discussions
- Ask questions in appropriate channels
- Provide detailed error information
- Be patient and persistent

---

## Recognition

### Contributors
- All contributors are recognized in CONTRIBUTORS.md
- Major contributors are highlighted in releases
- Contributions are tracked in commit history
- Special recognition for maintainers

### Recognition Criteria
- Code contributions
- Documentation improvements
- Bug reports and fixes
- Community support
- Design and UX improvements

---

## Support

For contributing support:
- **Documentation**: [Development Setup](development-setup.md)
- **Code Structure**: [Code Structure](code-structure.md)
- **Testing**: [Testing Guide](testing.md)
- **Troubleshooting**: [Troubleshooting Guide](../10-reference/troubleshooting.md)
- **Email**: autobotsolution@gmail.com

---

## License

By contributing to Valtronics, you agree that your contributions will be licensed under the same license as the project.

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**Contributing Guidelines v1.0**
