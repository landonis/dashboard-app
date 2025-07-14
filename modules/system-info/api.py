#!/usr/bin/env python3

import os
import platform
import psutil
import socket
from datetime import datetime
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import User
import logging

logger = logging.getLogger(__name__)

# Create blueprint
system_info_bp = Blueprint('system_info', __name__)

def admin_required(f):
    """Decorator to require admin access"""
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@system_info_bp.route('/system-info', methods=['GET'])
@jwt_required()
@admin_required
def get_system_info():
    """Get comprehensive system information"""
    try:
        # Get system uptime
        boot_time = psutil.boot_time()
        uptime_seconds = datetime.now().timestamp() - boot_time
        
        # Get CPU information
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Get memory information
        memory = psutil.virtual_memory()
        memory_info = {
            'total': memory.total,
            'used': memory.used,
            'free': memory.available,
            'percentage': memory.percent
        }
        
        # Get disk information
        disk = psutil.disk_usage('/')
        disk_info = {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percentage': (disk.used / disk.total) * 100
        }
        
        # Get load average (Unix systems only)
        load_avg = []
        try:
            load_avg = list(os.getloadavg())
        except (OSError, AttributeError):
            # Windows doesn't support getloadavg
            load_avg = [0.0, 0.0, 0.0]
        
        # Get process count
        process_count = len(psutil.pids())
        
        # Get network information
        hostname = socket.gethostname()
        
        # Get platform information
        platform_info = platform.system()
        
        system_info = {
            'uptime': str(int(uptime_seconds)),
            'cpu_usage': cpu_percent,
            'cpu_count': cpu_count,
            'memory_usage': memory_info,
            'disk_usage': disk_info,
            'load_average': load_avg,
            'processes': process_count,
            'hostname': hostname,
            'platform': platform_info,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info("System information retrieved successfully")
        return jsonify(system_info)
        
    except Exception as e:
        logger.error(f"System info error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve system information'}), 500

@system_info_bp.route('/system-info/processes', methods=['GET'])
@jwt_required()
@admin_required
def get_processes():
    """Get running processes information"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                process_info = proc.info
                processes.append({
                    'pid': process_info['pid'],
                    'name': process_info['name'],
                    'cpu_percent': process_info['cpu_percent'],
                    'memory_percent': process_info['memory_percent'],
                    'status': process_info['status']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Process may have terminated or access denied
                continue
        
        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        
        logger.info("Process information retrieved successfully")
        return jsonify(processes[:20])  # Return top 20 processes
        
    except Exception as e:
        logger.error(f"Process info error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve process information'}), 500

@system_info_bp.route('/system-info/network', methods=['GET'])
@jwt_required()
@admin_required
def get_network_info():
    """Get network interface information"""
    try:
        network_info = {}
        
        # Get network interfaces
        interfaces = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        
        for interface_name, addresses in interfaces.items():
            interface_info = {
                'addresses': [],
                'stats': {}
            }
            
            # Get addresses
            for addr in addresses:
                address_info = {
                    'family': str(addr.family),
                    'address': addr.address,
                    'netmask': addr.netmask,
                    'broadcast': addr.broadcast
                }
                interface_info['addresses'].append(address_info)
            
            # Get stats
            if interface_name in stats:
                stat = stats[interface_name]
                interface_info['stats'] = {
                    'isup': stat.isup,
                    'duplex': str(stat.duplex),
                    'speed': stat.speed,
                    'mtu': stat.mtu
                }
            
            network_info[interface_name] = interface_info
        
        logger.info("Network information retrieved successfully")
        return jsonify(network_info)
        
    except Exception as e:
        logger.error(f"Network info error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve network information'}), 500