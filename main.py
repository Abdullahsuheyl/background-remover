import tkinter as tk
from tkinter import filedialog, Scale
from rembg import remove, new_session
from PIL import Image, ImageTk
import os
from rembg.session_factory import new_session
from rembg.bg import remove

class ArkaplanKaldirici:
    def __init__(self, root):
        self.root = root
        self.root.title("Gelişmiş Arka Plan Kaldırma Uygulaması")
        
        # Model ayarları
        self.model_params = {
            "alpha_matting": True,
            "alpha_matting_foreground_threshold": 240,
            "alpha_matting_background_threshold": 10,
            "alpha_matting_erode_size": 10
        }
        
        # Kontrol paneli
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(pady=10)
        
        # Alpha matting ayarları
        self.alpha_var = tk.BooleanVar(value=True)
        self.alpha_check = tk.Checkbutton(self.control_frame, 
                                        text="Alpha Matting", 
                                        variable=self.alpha_var,
                                        command=self.update_params)
        self.alpha_check.pack()
        
        # Hassasiyet ayarı
        tk.Label(self.control_frame, text="Hassasiyet:").pack()
        self.threshold_scale = Scale(self.control_frame, 
                                   from_=0, to=100, 
                                   orient=tk.HORIZONTAL,
                                   command=self.update_params)
        self.threshold_scale.set(50)
        self.threshold_scale.pack()
        
        # Kenar yumuşatma ayarı
        tk.Label(self.control_frame, text="Kenar Yumuşatma:").pack()
        self.erode_scale = Scale(self.control_frame, 
                                from_=1, to=20, 
                                orient=tk.HORIZONTAL,
                                command=self.update_params)
        self.erode_scale.set(10)
        self.erode_scale.pack()
        
        # Ek kalite ayarları
        self.quality_frame = tk.Frame(self.control_frame)
        self.quality_frame.pack(pady=5)
        
        tk.Label(self.quality_frame, text="Görüntü Kalitesi:").pack()
        self.quality_scale = Scale(self.quality_frame, 
                                 from_=1, to=100, 
                                 orient=tk.HORIZONTAL,
                                 command=self.update_params)
        self.quality_scale.set(95)
        self.quality_scale.pack()
        
        # Ana butonlar
        self.resim_sec_btn = tk.Button(root, text="Resim Seç", command=self.resim_sec)
        self.resim_sec_btn.pack(pady=5)
        
        self.islem_btn = tk.Button(root, text="Arka Planı Kaldır", command=self.arkaplan_kaldir)
        self.islem_btn.pack(pady=5)
        
        # Resim gösterme alanları
        self.frame = tk.Frame(root)
        self.frame.pack()
        
        self.original_label = tk.Label(self.frame)
        self.original_label.pack(side=tk.LEFT, padx=10)
        
        self.processed_label = tk.Label(self.frame)
        self.processed_label.pack(side=tk.LEFT, padx=10)
        
        self.dosya_yolu = None
        
        # Özel model oturumu oluştur
        self.session = new_session("isnet-general-use")
        
    def update_params(self, *args):
        self.model_params.update({
            "alpha_matting": self.alpha_var.get(),
            "alpha_matting_foreground_threshold": int(240 * (self.threshold_scale.get() / 100)),
            "alpha_matting_background_threshold": int(10 * (self.threshold_scale.get() / 100)),
            "alpha_matting_erode_size": self.erode_scale.get()
        })
        
    def resim_sec(self):
        self.dosya_yolu = filedialog.askopenfilename(
            filetypes=[("Resim Dosyaları", "*.png *.jpg *.jpeg")]
        )
        if self.dosya_yolu:
            resim = Image.open(self.dosya_yolu)
            resim = resim.resize((300, 300))
            photo = ImageTk.PhotoImage(resim)
            self.original_label.configure(image=photo)
            self.original_label.image = photo
            
    def arkaplan_kaldir(self):
        if self.dosya_yolu:
            input_image = Image.open(self.dosya_yolu)
            
            # Ön işleme: Görüntüyü optimize et
            input_image = input_image.convert('RGB')
            
            # Gelişmiş arka plan kaldırma
            output_image = remove(
                input_image,
                session=self.session,
                alpha_matting=self.model_params["alpha_matting"],
                alpha_matting_foreground_threshold=self.model_params["alpha_matting_foreground_threshold"],
                alpha_matting_background_threshold=self.model_params["alpha_matting_background_threshold"],
                alpha_matting_erode_size=self.model_params["alpha_matting_erode_size"],
                post_process_mask=True  # Kenar iyileştirmesi için
            )
            
            # Son işleme: Görüntü kalitesini artır
            output_image = output_image.convert('RGBA')
            
            # Görüntüyü kaydet
            dosya_adi = os.path.splitext(self.dosya_yolu)[0]
            output_image.save(
                f"{dosya_adi}_arkaplan_kaldirilmis.png",
                "PNG",
                quality=self.quality_scale.get(),
                optimize=True
            )
            
            # Önizleme için yeniden boyutlandır
            output_preview = output_image.copy()
            output_preview.thumbnail((300, 300))
            photo = ImageTk.PhotoImage(output_preview)
            self.processed_label.configure(image=photo)
            self.processed_label.image = photo

if __name__ == "__main__":
    root = tk.Tk()
    app = ArkaplanKaldirici(root)
    root.mainloop()
