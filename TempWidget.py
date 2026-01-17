import tkinter as tk
from tkinter import ttk, messagebox
import requests
import re

class TempWidget:
    def __init__(self, root):
        self.root = root
        self.root.title("Temperature Widget")
        self.root.geometry("300x190")
        self.root.attributes('-topmost', True)  # Keep window on top
        self.root.configure(bg='#2c3e50')
        
        # Synoptic Data API key  You can get this for free at https://synopticdata.com/
        self.synoptic_api_key = "YOUR_API_KEY"
        
        # Title
        title_label = tk.Label(root, text="Temperature Widget", 
                              font=('Arial', 12, 'bold'),
                              bg='#2c3e50', fg='white')
        title_label.pack(pady=5)
        
        # Input entry
        input_frame = tk.Frame(root, bg='#2c3e50')
        input_frame.pack(pady=5)
        
        tk.Label(input_frame, text="Zipcode or Station:", bg='#2c3e50', fg='white').pack(side=tk.LEFT)
        self.input_entry = tk.Entry(input_frame, width=12)
        self.input_entry.pack(side=tk.LEFT, padx=5)
        
        update_btn = tk.Button(input_frame, text="Update", command=self.update_temp)
        update_btn.pack(side=tk.LEFT)
        
        # Help text
        help_label = tk.Label(root, text="Examples: 83013, KJAC, D0414", 
                             font=('Arial', 7),
                             bg='#2c3e50', fg='#95a5a6')
        help_label.pack()
        
        # Location display
        self.location_label = tk.Label(root, text="Enter zipcode or station", 
                                       font=('Arial', 10, 'bold'),
                                       bg='#2c3e50', fg='#ecf0f1')
        self.location_label.pack(pady=2)
        
        # Temperature display
        self.temp_label = tk.Label(root, text="", 
                                   font=('Arial', 20, 'bold'),
                                   bg='#2c3e50', fg='#ecf0f1')
        self.temp_label.pack(pady=5)
        
        # Last update time
        self.update_time_label = tk.Label(root, text="", 
                                         font=('Arial', 8),
                                         bg='#2c3e50', fg='#95a5a6')
        self.update_time_label.pack()
    
    def is_zipcode(self, input_str):
        """Check if input is a zipcode (5 digits)"""
        return bool(re.match(r'^\d{5}$', input_str))
    
    def get_temp_from_zipcode(self, zipcode):
        """Get temperature using zipcode via Synoptic API"""
        try:
            # First get coordinates from zipcode using zippopotam
            zip_url = f"https://api.zippopotam.us/us/{zipcode}"
            zip_response = requests.get(zip_url, timeout=5)
            
            if zip_response.status_code != 200:
                messagebox.showerror("Error", f"Zipcode '{zipcode}' not found")
                return None
            
            zip_data = zip_response.json()
            lat = float(zip_data['places'][0]['latitude'])
            lon = float(zip_data['places'][0]['longitude'])
            city = zip_data['places'][0]['place name']
            state = zip_data['places'][0]['state abbreviation']
            location_name = f"{city}, {state}"
            
            # Now use Synoptic API with lat/lon coordinates
            synoptic_url = "https://api.synopticdata.com/v2/stations/latest"
            params = {
                'token': self.synoptic_api_key,
                'radius': f'{lat},{lon},50',  # lat,lon,radius_in_miles
                'limit': 1,
                'vars': 'air_temp'
            }
            
            response = requests.get(synoptic_url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['SUMMARY']['RESPONSE_CODE'] == 1 and data['STATION']:
                    station = data['STATION'][0]
                    
                    if 'air_temp_value_1' in station['OBSERVATIONS']:
                        temp_c = station['OBSERVATIONS']['air_temp_value_1']['value']
                        temp_c = round(temp_c)
                        temp_f = round(temp_c * 9/5 + 32)
                        
                        return temp_c, temp_f, location_name, zipcode
                    else:
                        messagebox.showerror("Error", f"No temperature data available near {zipcode}")
                        return None
                else:
                    messagebox.showerror("Error", f"No weather stations found near {zipcode}")
                    return None
            else:
                messagebox.showerror("Error", f"API request failed")
                return None
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            return None
    
    def get_synoptic_temperature(self, station_id):
        """Fetch temperature from any station via Synoptic Data API"""
        try:
            synoptic_url = "https://api.synopticdata.com/v2/stations/latest"
            params = {
                'token': self.synoptic_api_key,
                'stid': station_id,
                'vars': 'air_temp'
            }
            
            response = requests.get(synoptic_url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['SUMMARY']['RESPONSE_CODE'] == 1 and data['STATION']:
                    station = data['STATION'][0]
                    station_name = station['NAME']
                    
                    if 'air_temp_value_1' in station['OBSERVATIONS']:
                        temp_c = station['OBSERVATIONS']['air_temp_value_1']['value']
                        temp_c = round(temp_c)
                        temp_f = round(temp_c * 9/5 + 32)
                        
                        return temp_c, temp_f, station_name, station_id.upper()
                    else:
                        messagebox.showerror("Error", f"No temperature data available for {station_id}")
                        return None
                else:
                    messagebox.showerror("Error", f"Station '{station_id}' not found")
                    return None
            else:
                messagebox.showerror("Error", f"API request failed with status {response.status_code}")
                return None
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            return None
    
    def update_temp(self):
        """Update the temperature display"""
        user_input = self.input_entry.get().strip().upper()
        
        if not user_input:
            messagebox.showwarning("Input Required", "Please enter a zipcode or station ID")
            return
        
        # Determine input type and fetch data
        if self.is_zipcode(user_input):
            result = self.get_temp_from_zipcode(user_input)
        else:
            # All station IDs use Synoptic API
            result = self.get_synoptic_temperature(user_input)
        
        if result:
            temp_c, temp_f, location_name, identifier = result
            
            self.location_label.config(text=location_name)
            self.temp_label.config(text=f"{temp_c}°C / {temp_f}°F")
            self.root.title(f"Temperature - {identifier}")
            
            from datetime import datetime
            current_time = datetime.now().strftime("%I:%M %p")
            self.update_time_label.config(text=f"Updated: {current_time}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TempWidget(root)
    root.mainloop()