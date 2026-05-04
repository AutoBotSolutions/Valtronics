# STM32 Platform Firmware

**STM32-based firmware for Valtronics industrial IoT devices**

---

## Overview

STM32 provides a professional-grade platform for Valtronics industrial devices, offering high performance, extensive peripherals, and robust reliability for demanding applications. This platform is ideal for industrial sensors, gateway devices, and high-performance monitoring equipment.

---

## Features

### Hardware Features
- **CPU**: ARM Cortex-M4/M7 (32-bit, up to 480 MHz)
- **Memory**: Up to 2 MB Flash, 512 KB SRAM
- **Peripherals**: Extensive GPIO, ADC/DAC, I2C, SPI, UART, CAN, Ethernet
- **Connectivity**: Built-in Ethernet, USB, CAN bus
- **Industrial**: Wide temperature range, EMI protection
- **Security**: Hardware encryption, secure boot, tamper detection

### Software Features
- **Framework**: STM32CubeIDE, STM32CubeMX, HAL/LL drivers
- **RTOS**: FreeRTOS support for real-time applications
- **Connectivity**: LwIP TCP/IP stack, mbed TLS
- **Security**: Hardware crypto acceleration, secure boot
- **Industrial**: Modbus, CAN bus, industrial protocols

---

## Supported Boards

### STM32F4 Series
- **STM32F407VGT6**: High-performance with Ethernet
- **STM32F429IGT6**: Advanced with LCD interface
- **STM32F411CEU6**: Compact with USB

### STM32F7 Series
- **STM32F767IGT6**: High-performance with Ethernet
- **STM32F746NGH6**: Advanced with LCD and Ethernet

### STM32H7 Series
- **STM32H743VIT6**: Ultra-high performance
- **STM32H747XIHX**: Dual-core with extensive peripherals

---

## Directory Structure

```
platform/stm32/
├── README.md                    # This file
├── platformio.ini               # PlatformIO configuration
├── src/                         # Source code
│   ├── main.cpp                 # Main application
│   ├── config/                  # Configuration
│   ├── drivers/                  # Hardware drivers
│   ├── sensors/                  # Sensor interfaces
│   ├── communication/            # Communication protocols
│   ├── rtos/                    # RTOS components
│   └── utils/                    # Utility functions
├── lib/                         # Libraries
├── test/                        # Tests
├── docs/                        # Documentation
└── examples/                    # Example implementations
```

---

## Quick Start

### 1. Setup Development Environment
```bash
# Install STM32CubeIDE
# Download from https://www.st.com/en/development-tools/stm32cubeide.html

# Or use PlatformIO with STM32 support
pip install platformio
pio platform install ststm32
```

### 2. Create New Project
```bash
# Using PlatformIO
pio project init --board nucleo_f429zi

# Using STM32CubeIDE
# File -> New -> STM32 Project
# Select board and configure peripherals
```

### 3. Configure Project
```ini
# platformio.ini
[env:nucleo_f429zi]
platform = ststm32
board = nucleo_f429zi
framework = stm32cube
build_flags = 
    -DUSE_HAL_DRIVER
    -DSTM32F429xx
    -DUSE_FULL_LL_DRIVER
    -DHSE_VALUE=8000000U
    -DUSE_STM32F4XX_NUCLEO_144
lib_deps = 
    stm32cube/stm32f4xx_hal_driver
    stm32cube/stm32f4xx_ll_driver
    stm32cube/freertos
    stm32cube/lwip
    stm32cube/mbedtls
```

### 4. Write Firmware
```cpp
#include "stm32f4xx_hal.h"
#include "stm32f4xx_hal_eth.h"
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"
#include "semphr.h"

// Device configuration
#define DEVICE_ID "VT-STM32-001"
#define MQTT_CLIENT_ID "VT-STM32-001"
#define MQTT_BROKER "mqtt.valtronics.com"
#define MQTT_PORT 1883

// Global variables
UART_HandleTypeDef huart2;
ETH_HandleTypeDef heth;
QueueHandle_t telemetry_queue;
SemaphoreHandle_t i2c_mutex;

void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_USART2_UART_Init(void);
static void MX_ETH_Init(void);

void main(void) {
    // HAL initialization
    HAL_Init();
    
    // Configure system clock
    SystemClock_Config();
    
    // Initialize peripherals
    MX_GPIO_Init();
    MX_USART2_UART_Init();
    MX_ETH_Init();
    
    // Initialize FreeRTOS
    telemetry_queue = xQueueCreate(10, sizeof(telemetry_data_t));
    i2c_mutex = xSemaphoreCreateMutex();
    
    // Create tasks
    xTaskCreate(sensor_task, "SensorTask", 512, NULL, 1, NULL);
    xTaskCreate(mqtt_task, "MQTTTask", 1024, NULL, 2, NULL);
    xTaskCreate(ethernet_task, "EthernetTask", 1024, NULL, 1, NULL);
    
    // Start scheduler
    vTaskStartScheduler();
    
    while (1) {
        // Should never reach here
    }
}

void sensor_task(void* parameters) {
    telemetry_data_t data;
    
    while (1) {
        // Read sensors
        data.temperature = read_temperature();
        data.humidity = read_humidity();
        data.pressure = read_pressure();
        data.timestamp = HAL_GetTick();
        
        // Send to queue
        xQueueSend(telemetry_queue, &data, portMAX_DELAY);
        
        // Delay for next reading
        vTaskDelay(pdMS_TO_TICKS(30000));  // 30 seconds
    }
}

void mqtt_task(void* parameters) {
    telemetry_data_t data;
    
    // Initialize MQTT client
    mqtt_client_init();
    
    while (1) {
        // Receive from queue
        if (xQueueReceive(telemetry_queue, &data, portMAX_DELAY)) {
            // Process and send telemetry
            send_telemetry(data);
        }
    }
}

void ethernet_task(void* parameters) {
    // Initialize Ethernet
    if (ethernet_init() == 0) {
        // Start DHCP client
        dhcp_init();
        
        while (1) {
            // Handle Ethernet events
            ethernet_handle_events();
            vTaskDelay(pdMS_TO_TICKS(100));
        }
    }
}
```

---

## Sensor Integration

### I2C Sensor (BME280)
```cpp
#include "stm32f4xx_hal_i2c.h"

I2C_HandleTypeDef hi2c1;

#define BME280_ADDRESS 0x76

void MX_I2C1_Init(void) {
    hi2c1.Instance = I2C1;
    hi2c1.Init.ClockSpeed = 100000;
    hi2c1.Init.DutyCycle = I2C_DUTYCYCLE_2;
    hi2c1.Init.OwnAddress1 = 0;
    hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
    hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
    hi2c1.Init.OwnAddress2 = 0;
    hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
    hi2c1.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
    
    if (HAL_I2C_Init(&hi2c1) != HAL_OK) {
        Error_Handler();
    }
}

bool bme280_init(void) {
    uint8_t chip_id = 0;
    
    // Read chip ID
    if (HAL_I2C_Mem_Read(&hi2c1, BME280_ADDRESS, 0xD0, 1, &chip_id, 1, HAL_MAX_DELAY) != HAL_OK) {
        return false;
    }
    
    if (chip_id != 0x60) {
        return false;
    }
    
    // Configure sensor
    uint8_t config[4] = {0x60, 0x90, 0x00, 0x02};  // Humidity, pressure, temperature config
    if (HAL_I2C_Mem_Write(&hi2c1, BME280_ADDRESS, 0xF2, 4, config, HAL_MAX_DELAY) != HAL_OK) {
        return false;
    }
    
    return true;
}

bool bme280_read_data(float* temperature, float* humidity, float* pressure) {
    uint8_t data[8];
    
    // Read sensor data
    if (HAL_I2C_Mem_Read(&hi2c1, BME280_ADDRESS, 0xF7, 8, data, HAL_MAX_DELAY) != HAL_OK) {
        return false;
    }
    
    // Convert raw data
    uint32_t press_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4);
    uint32_t temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4);
    uint16_t hum_raw = (data[6] << 8) | data[7];
    
    // Apply calibration (simplified)
    *temperature = (float)temp_raw / 5120.0 - 64.0;
    *pressure = (float)press_raw / 25600.0;
    *humidity = (float)hum_raw / 1024.0;
    
    return true;
}
```

### SPI Sensor (PMS5003)
```cpp
#include "stm32f4xx_hal_spi.h"

SPI_HandleTypeDef hspi1;

#define PMS5003_CS_PIN GPIO_PIN_4
#define PMS5003_CS_PORT GPIOA

void MX_SPI1_Init(void) {
    hspi1.Instance = SPI1;
    hspi1.Init.Mode = SPI_MODE_MASTER;
    hspi1.Init.Direction = SPI_DIRECTION_2LINES;
    hspi1.Init.DataSize = SPI_DATASIZE_8BIT;
    hspi1.Init.CLKPolarity = SPI_POLARITY_LOW;
    hspi1.Init.CLKPhase = SPI_PHASE_1EDGE;
    hspi1.Init.NSS = SPI_NSS_SOFT;
    hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_64;
    hspi1.Init.FirstBit = SPI_FIRSTBIT_MSB;
    hspi1.Init.TIMode = SPI_TIMODE_DISABLE;
    hspi1.Init.CRCCalculation = SPI_CRCCALCULATION_DISABLE;
    
    if (HAL_SPI_Init(&hspi1) != HAL_OK) {
        Error_Handler();
    }
}

void pms5003_cs_select(void) {
    HAL_GPIO_WritePin(PMS5003_CS_PORT, PMS5003_CS_PIN, GPIO_PIN_RESET);
}

void pms5003_cs_deselect(void) {
    HAL_GPIO_WritePin(PMS5003_CS_PORT, PMS5003_CS_PIN, GPIO_PIN_SET);
}

bool pms5003_read_data(uint16_t* pm25, uint16_t* pm10) {
    uint8_t tx_data[1] = {0x42};
    uint8_t rx_data[32];
    
    pms5003_cs_select();
    
    // Send start command
    if (HAL_SPI_TransmitReceive(&hspi1, tx_data, rx_data, 1, HAL_MAX_DELAY) != HAL_OK) {
        pms5003_cs_deselect();
        return false;
    }
    
    // Read data
    if (HAL_SPI_Receive(&hspi1, rx_data, 32, HAL_MAX_DELAY) != HAL_OK) {
        pms5003_cs_deselect();
        return false;
    }
    
    pms5003_cs_deselect();
    
    // Validate data
    if (rx_data[0] != 0x42 || rx_data[1] != 0x4D) {
        return false;
    }
    
    // Calculate checksum
    uint16_t checksum = 0;
    for (int i = 0; i < 30; i++) {
        checksum += rx_data[i];
    }
    
    if ((checksum >> 8) != rx_data[30] || (checksum & 0xFF) != rx_data[31]) {
        return false;
    }
    
    // Extract PM2.5 and PM10
    *pm25 = (rx_data[12] << 8) | rx_data[13];
    *pm10 = (rx_data[14] << 8) | rx_data[15];
    
    return true;
}
```

---

## Communication Protocols

### Ethernet with LwIP
```cpp
#include "lwip/opt.h"
#include "lwip/tcp.h"
#include "lwip/dhcp.h"
#include "netif/ethernet.h"

struct netif gnetif;

void ethernet_init(void) {
    struct ip_addr ipaddr;
    struct ip_addr netmask;
    struct ip_addr gw;
    
    // Initialize LwIP
    tcpip_init(NULL, NULL);
    
    // Create netif
    netif_add(&gnetif, &ipaddr, &netmask, &gw, NULL, ethernetif_init, ethernet_input);
    
    // Set as default netif
    netif_set_default(&gnetif);
    
    // Set link up
    netif_set_link_up(&gnetif);
    
    // Start DHCP client
    dhcp_start(&gnetif);
}

void ethernet_handle_events(void) {
    // Handle LwIP timers
    sys_check_timeouts();
    
    // Handle Ethernet input
    if (HAL_ETH_GetReceivedFrame_IT(&heth) == HAL_OK) {
        ethernetif_input(&gnetif);
    }
}

bool mqtt_connect_stm32(const char* broker, uint16_t port) {
    struct sockaddr_in server_addr;
    int sockfd;
    
    // Create socket
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        return false;
    }
    
    // Configure server address
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    inet_aton(broker, &server_addr.sin_addr);
    
    // Connect to server
    if (connect(sockfd, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        close(sockfd);
        return false;
    }
    
    // Send MQTT connect packet
    uint8_t connect_packet[] = {
        0x10,  // CONNECT packet type
        0x10,  // Remaining length
        0x00, 0x04,  // Protocol name length
        'M', 'Q', 'T', 'T',  // Protocol name
        0x04,  // Protocol version
        0x02,  // Connect flags
        0x00, 0x3C,  // Keep alive
        0x00, 0x0C,  // Client ID length
        'V', 'T', '-', 'S', 'T', 'M', '3', '2', '-', '0', '0', '1'
    };
    
    if (send(sockfd, connect_packet, sizeof(connect_packet), 0) < 0) {
        close(sockfd);
        return false;
    }
    
    // Wait for CONNACK
    uint8_t connack[4];
    if (recv(sockfd, connack, 4, 0) < 4) {
        close(sockfd);
        return false;
    }
    
    if (connack[0] != 0x20 || connack[2] != 0x00) {
        close(sockfd);
        return false;
    }
    
    close(sockfd);
    return true;
}
```

### CAN Bus Communication
```cpp
#include "stm32f4xx_hal_can.h"

CAN_HandleTypeDef hcan;

void MX_CAN1_Init(void) {
    hcan.Instance = CAN1;
    hcan.Init.Prescaler = 9;
    hcan.Init.Mode = CAN_MODE_NORMAL;
    hcan.Init.SJW = CAN_SJW_1TQ;
    hcan.Init.BS1 = CAN_BS1_2TQ;
    hcan.Init.BS2 = CAN_BS2_3TQ;
    hcan.Init.TTCM = DISABLE;
    hcan.Init.ABOM = DISABLE;
    hcan.Init.AWUM = DISABLE;
    hcan.Init.NART = DISABLE;
    hcan.Init.RFLM = DISABLE;
    hcan.Init.TXFP = DISABLE;
    
    if (HAL_CAN_Init(&hcan) != HAL_OK) {
        Error_Handler();
    }
    
    // Configure CAN filters
    CAN_FilterTypeDef sFilterConfig;
    sFilterConfig.FilterBank = 0;
    sFilterConfig.FilterMode = CAN_FILTERMODE_IDMASK;
    sFilterConfig.FilterScale = CAN_FILTERSCALE_32BIT;
    sFilterConfig.FilterIdHigh = 0x0000;
    sFilterConfig.FilterIdLow = 0x0000;
    sFilterConfig.FilterMaskIdHigh = 0x0000;
    sFilterConfig.FilterMaskIdLow = 0x0000;
    sFilterConfig.FilterFIFOAssignment = CAN_RX_FIFO0;
    sFilterConfig.FilterActivation = ENABLE;
    sFilterConfig.BankNumber = 14;
    
    if (HAL_CAN_ConfigFilter(&hcan, &sFilterConfig) != HAL_OK) {
        Error_Handler();
    }
    
    // Start CAN
    if (HAL_CAN_Start(&hcan) != HAL_OK) {
        Error_Handler();
    }
}

bool can_send_telemetry(uint32_t can_id, const uint8_t* data, uint8_t length) {
    CAN_TxHeaderTypeDef tx_header;
    uint32_t tx_mailbox;
    
    tx_header.StdId = can_id;
    tx_header.ExtId = 0;
    tx_header.RTR = CAN_RTR_DATA;
    tx_header.IDE = CAN_ID_STD;
    tx_header.DLC = length;
    tx_header.TransmitGlobalTime = DISABLE;
    
    if (HAL_CAN_AddTxMessage(&hcan, &tx_header, data, &tx_mailbox) != HAL_OK) {
        return false;
    }
    
    return true;
}

bool can_receive_telemetry(uint32_t* can_id, uint8_t* data, uint8_t* length) {
    CAN_RxHeaderTypeDef rx_header;
    
    if (HAL_CAN_GetRxMessage(&hcan, CAN_RX_FIFO0, &rx_header, data, length) != HAL_OK) {
        return false;
    }
    
    *can_id = rx_header.StdId;
    return true;
}
```

---

## Power Management

### Low Power Modes
```cpp
#include "stm32f4xx_hal_pwr.h"

void enter_stop_mode(void) {
    // Configure wake-up sources
    HAL_PWR_EnableWakeUpPin(PWR_WAKEUP_PIN1);
    
    // Enter stop mode
    HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_STOPENTRY_WFI);
    
    // Wake up from stop mode
    SystemClock_Config();
}

void enter_standby_mode(void) {
    // Configure wake-up sources
    HAL_PWR_EnableWakeUpPin(PWR_WAKEUP_PIN1);
    
    // Clear wake-up flag
    __HAL_PWR_CLEAR_FLAG(PWR_FLAG_WU);
    
    // Enter standby mode
    HAL_PWR_EnterSTANDBYMode();
}

void configure_clock_for_low_power(void) {
    // Switch to MSI clock
    RCC_OscInitTypeDef RCC_OscInitStruct;
    RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_MSI;
    RCC_OscInitStruct.MSIState = RCC_MSI_ON;
    RCC_OscInitStruct.MSICalibrationValue = RCC_MSICALIBRATION_DEFAULT;
    RCC_OscInitStruct.MSIClockRange = RCC_MSIRANGE_6;
    RCC_OscInitStruct.PLL.PLLState = RCC_PLL_NONE;
    
    HAL_RCC_OscConfig(&RCC_OscInitStruct);
    
    // Update system clock
    RCC_ClkInitTypeDef RCC_ClkInitStruct;
    RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
    RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_MSI;
    RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
    RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
    RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;
    
    HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_0);
}
```

### Battery Monitoring
```cpp
#include "stm32f4xx_hal_adc.h"

ADC_HandleTypeDef hadc1;

#define BATTERY_ADC_CHANNEL ADC_CHANNEL_0

void MX_ADC1_Init(void) {
    ADC_ChannelConfTypeDef sConfig = {0};
    
    hadc1.Instance = ADC1;
    hadc1.Init.ClockPrescaler = ADC_CLOCK_SYNC_PCLK_DIV4;
    hadc1.Init.Resolution = ADC_RESOLUTION_12B;
    hadc1.Init.ScanConvMode = DISABLE;
    hadc1.Init.ContinuousConvMode = DISABLE;
    hadc1.Init.DiscontinuousConvMode = DISABLE;
    hadc1.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;
    hadc1.Init.ExternalTrigConv = ADC_SOFTWARE_START;
    hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
    hadc1.Init.NbrOfConversion = 1;
    
    if (HAL_ADC_Init(&hadc1) != HAL_OK) {
        Error_Handler();
    }
    
    sConfig.Channel = BATTERY_ADC_CHANNEL;
    sConfig.Rank = 1;
    sConfig.SamplingTime = ADC_SAMPLETIME_480CYCLES;
    
    if (HAL_ADC_ConfigChannel(&hadc1, &sConfig, 1) != HAL_OK) {
        Error_Handler();
    }
}

float read_battery_voltage(void) {
    uint32_t adc_value;
    float voltage;
    
    // Start ADC conversion
    HAL_ADC_Start(&hadc1);
    
    // Wait for conversion complete
    if (HAL_ADC_PollForConversion(&hadc1, HAL_MAX_DELAY) == HAL_OK) {
        adc_value = HAL_ADC_GetValue(&hadc1);
        
        // Convert ADC value to voltage (assuming 3.3V reference)
        voltage = (float)adc_value * 3.3 / 4096.0;
        
        // Apply voltage divider factor (if used)
        voltage *= 2.0;  // Example: 1:1 voltage divider
    } else {
        voltage = 0.0;
    }
    
    // Stop ADC
    HAL_ADC_Stop(&hadc1);
    
    return voltage;
}

uint8_t get_battery_percentage(float voltage) {
    // Convert voltage to percentage (calibration required)
    if (voltage >= 4.2) return 100;
    if (voltage <= 3.0) return 0;
    
    // Linear approximation
    return (uint8_t)((voltage - 3.0) / (4.2 - 3.0) * 100);
}
```

---

## Security Features

### Hardware Encryption
```cpp
#include "stm32f4xx_hal_cryp.h"

CRYP_HandleTypeDef hcryp;

void MX_CRYP_Init(void) {
    hcryp.Instance = CRYP;
    hcryp.Init.DataType = CRYP_DATATYPE_8B;
    hcryp.Init.KeySize = CRYP_KEYSIZE_128B;
    hcryp.Init.DataWidthUnit = CRYP_DATAWIDTHUNIT_BYTE;
    hcryp.Init.Algorithm = CRYP_ALGORITHM_AES;
    hcryp.Init.KeyIVConfigSkip = CRYP_KEYIVCONFIG_SKIP_NONE;
    
    if (HAL_CRYP_Init(&hcryp) != HAL_OK) {
        Error_Handler();
    }
}

bool encrypt_data(const uint8_t* plaintext, uint8_t* ciphertext, const uint8_t* key) {
    // Set encryption key
    if (HAL_CRYP_SetKey(&hcryp, key, 16) != HAL_OK) {
        return false;
    }
    
    // Encrypt data
    if (HAL_CRYP_Encrypt(&hcryp, plaintext, 16, ciphertext, HAL_MAX_DELAY) != HAL_OK) {
        return false;
    }
    
    return true;
}

bool decrypt_data(const uint8_t* ciphertext, uint8_t* plaintext, const uint8_t* key) {
    // Set decryption key
    if (HAL_CRYP_SetKey(&hcryp, key, 16) != HAL_OK) {
        return false;
    }
    
    // Decrypt data
    if (HAL_CRYP_Decrypt(&hcryp, ciphertext, 16, plaintext, HAL_MAX_DELAY) != HAL_OK) {
        return false;
    }
    
    return true;
}
```

### Secure Boot
```cpp
#include "stm32f4xx_hal_flash.h"

bool verify_firmware_signature(const uint8_t* signature, const uint8_t* public_key) {
    // This is a simplified example
    // In practice, you would use ECC or RSA verification
    
    uint8_t firmware_hash[32];
    
    // Calculate firmware hash
    if (!calculate_firmware_hash(firmware_hash)) {
        return false;
    }
    
    // Verify signature (simplified)
    return verify_signature(firmware_hash, signature, public_key);
}

bool calculate_firmware_hash(uint8_t* hash) {
    // Calculate SHA-256 hash of firmware
    // This would use the hardware hash acceleration if available
    
    // Simplified implementation
    for (int i = 0; i < 32; i++) {
        hash[i] = 0;  // Placeholder
    }
    
    return true;
}

bool verify_signature(const uint8_t* hash, const uint8_t* signature, const uint8_t* public_key) {
    // Verify ECDSA or RSA signature
    // This would use the hardware crypto acceleration
    
    // Simplified implementation
    return true;
}
```

---

## Industrial Protocols

### Modbus RTU
```cpp
#include "stm32f4xx_hal_uart.h"

#define MODBUS_UART_HANDLE huart3

typedef struct {
    uint8_t address;
    uint8_t function;
    uint16_t register_address;
    uint16_t register_count;
    uint16_t crc;
} modbus_request_t;

bool modbus_read_holding_registers(uint8_t slave_addr, uint16_t reg_addr, uint16_t reg_count, uint16_t* data) {
    modbus_request_t request;
    uint8_t response[256];
    
    // Build request
    request.address = slave_addr;
    request.function = 0x03;  // Read Holding Registers
    request.register_address = reg_addr;
    request.register_count = reg_count;
    request.crc = calculate_modbus_crc((uint8_t*)&request, 6);
    
    // Send request
    if (HAL_UART_Transmit(&huart3, (uint8_t*)&request, 8, HAL_MAX_DELAY) != HAL_OK) {
        return false;
    }
    
    // Receive response
    if (HAL_UART_Receive(&huart3, response, 5 + reg_count * 2 + 2, HAL_MAX_DELAY) != HAL_OK) {
        return false;
    }
    
    // Validate response
    if (response[0] != slave_addr || response[1] != 0x03) {
        return false;
    }
    
    uint16_t received_crc = (response[response[1] + reg_count * 2 + 1] << 8) | response[response[1] + reg_count * 2];
    uint16_t calculated_crc = calculate_modbus_crc(response, 3 + reg_count * 2);
    
    if (received_crc != calculated_crc) {
        return false;
    }
    
    // Extract data
    for (int i = 0; i < reg_count; i++) {
        data[i] = (response[3 + i * 2] << 8) | response[4 + i * 2];
    }
    
    return true;
}

uint16_t calculate_modbus_crc(const uint8_t* data, uint16_t length) {
    uint16_t crc = 0xFFFF;
    
    for (int i = 0; i < length; i++) {
        crc ^= data[i];
        
        for (int j = 0; j < 8; j++) {
            if (crc & 0x0001) {
                crc = (crc >> 1) ^ 0xA001;
            } else {
                crc >>= 1;
            }
        }
    }
    
    return crc;
}
```

---

## Testing

### Unit Tests
```cpp
#include "unity.h"

void test_i2c_communication(void) {
    // Test I2C initialization
    TEST_ASSERT_EQUAL(HAL_OK, HAL_I2C_Init(&hi2c1));
    
    // Test sensor communication
    uint8_t chip_id = 0;
    TEST_ASSERT_EQUAL(HAL_OK, HAL_I2C_Mem_Read(&hi2c1, BME280_ADDRESS, 0xD0, 1, &chip_id, 1, HAL_MAX_DELAY));
    TEST_ASSERT_EQUAL(0x60, chip_id);
}

void test_ethernet_initialization(void) {
    // Test Ethernet initialization
    TEST_ASSERT_EQUAL(HAL_OK, HAL_ETH_Init(&heth));
    
    // Test network interface
    TEST_ASSERT_NOT_EQUAL(NULL, &gnetif);
}

void test_can_communication(void) {
    // Test CAN initialization
    TEST_ASSERT_EQUAL(HAL_OK, HAL_CAN_Init(&hcan));
    
    // Test message transmission
    uint8_t test_data[] = {0x01, 0x02, 0x03, 0x04};
    TEST_ASSERT_TRUE(can_send_telemetry(0x123, test_data, 4));
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_i2c_communication);
    RUN_TEST(test_ethernet_initialization);
    RUN_TEST(test_can_communication);
    return UNITY_END();
}
```

### Hardware Tests
```cpp
void run_hardware_tests(void) {
    printf("Running hardware tests...\n");
    
    // Test I2C sensors
    if (!test_i2c_sensors()) {
        printf("I2C sensor test failed\n");
    }
    
    // Test Ethernet
    if (!test_ethernet_connection()) {
        printf("Ethernet test failed\n");
    }
    
    // Test CAN bus
    if (!test_can_bus()) {
        printf("CAN bus test failed\n");
    }
    
    printf("Hardware tests completed\n");
}

bool test_i2c_sensors(void) {
    uint8_t devices_found = 0;
    
    // Scan I2C bus
    for (uint8_t addr = 0x08; addr <= 0x77; addr++) {
        if (HAL_I2C_IsDeviceReady(&hi2c1, addr, 1, HAL_MAX_DELAY) == HAL_OK) {
            printf("I2C device found at address: 0x%02X\n", addr);
            devices_found++;
        }
    }
    
    return devices_found > 0;
}
```

---

## Performance Optimization

### FreeRTOS Configuration
```cpp
#include "FreeRTOSConfig.h"

// Task priorities
#define SENSOR_TASK_PRIORITY        (tskIDLE_PRIORITY + 1)
#define MQTT_TASK_PRIORITY         (tskIDLE_PRIORITY + 2)
#define ETHERNET_TASK_PRIORITY      (tskIDLE_PRIORITY + 1)

// Stack sizes
#define SENSOR_TASK_STACK_SIZE      (512)
#define MQTT_TASK_STACK_SIZE       (1024)
#define ETHERNET_TASK_STACK_SIZE    (1024)

// Heap configuration
#define configTOTAL_HEAP_SIZE        (8192)
#define configMINIMAL_STACK_SIZE     (128)

// Timer configuration
#define configUSE_TIMERS             1
#define configTICK_RATE_HZ          (1000)

// Queue configuration
#define configUSE_QUEUE_SETS         1
#define configUSE_MUTEXES            1
#define configUSE_RECURSIVE_MUTEXES  1
```

### Memory Optimization
```cpp
// Use static allocation for critical data
static uint8_t sensor_buffer[256];
static uint8_t mqtt_buffer[512];

// Use memory pools for dynamic allocation
#define MEMORY_POOL_SIZE 1024
static uint8_t memory_pool[MEMORY_POOL_SIZE];
static size_t memory_pool_index = 0;

void* memory_pool_alloc(size_t size) {
    if (memory_pool_index + size > MEMORY_POOL_SIZE) {
        return NULL;
    }
    
    void* ptr = &memory_pool[memory_pool_index];
    memory_pool_index += size;
    
    return ptr;
}

void memory_pool_free(void* ptr) {
    // Simple implementation - doesn't actually free memory
    // In practice, you would implement a proper memory pool
}

// Use DMA for efficient data transfer
void setup_dma_for_uart(void) {
    // Configure DMA for UART transmission
    HAL_UART_Transmit_DMA(&huart2, (uint8_t*)"Hello World", 11);
}
```

---

## Troubleshooting

### Common Issues

#### Ethernet Connection Problems
```cpp
void debug_ethernet(void) {
    printf("Ethernet Debug:\n");
    
    // Check link status
    if (HAL_ETH_GetLinkState(&heth) == ETH_LINK_UP) {
        printf("Link status: UP\n");
    } else {
        printf("Link status: DOWN\n");
    }
    
    // Check IP configuration
    printf("IP address: %s\n", ip4addr_ntoa(&gnetif.ip_addr));
    printf("Netmask: %s\n", ip4addr_ntoa(&gnetif.netmask));
    printf("Gateway: %s\n", ip4addr_ntoa(&gnetif.gw));
    
    // Check MAC address
    uint8_t mac_addr[6];
    HAL_ETH_GetMACAddress(&heth, mac_addr);
    printf("MAC address: %02X:%02X:%02X:%02X:%02X:%02X\n",
           mac_addr[0], mac_addr[1], mac_addr[2], mac_addr[3], mac_addr[4], mac_addr[5]);
}
```

#### I2C Communication Issues
```cpp
void debug_i2c(void) {
    printf("I2C Debug:\n");
    
    // Check I2C state
    printf("I2C state: %d\n", hi2c1.State);
    
    // Scan I2C bus
    printf("Scanning I2C bus...\n");
    for (uint8_t addr = 0x08; addr <= 0x77; addr++) {
        if (HAL_I2C_IsDeviceReady(&hi2c1, addr, 1, HAL_MAX_DELAY) == HAL_OK) {
            printf("Device found at 0x%02X\n", addr);
        }
    }
    
    // Test specific sensor
    uint8_t chip_id = 0;
    HAL_StatusTypeDef status = HAL_I2C_Mem_Read(&hi2c1, BME280_ADDRESS, 0xD0, 1, &chip_id, 1, HAL_MAX_DELAY);
    printf("BME280 read status: %d\n", status);
    printf("BME280 chip ID: 0x%02X\n", chip_id);
}
```

---

## Support

For STM32 firmware support:
- **Documentation**: See `docs/` directory
- **Examples**: See `examples/` directory
- **Platform Guides**: See `platform/*/` directories
- **ST Documentation**: STM32CubeIDE and HAL documentation
- **Email**: firmware@valtronics.com

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**STM32 Platform Firmware v1.0**
