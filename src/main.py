import random
import time
import threading
import tkinter as tk


class Mall:
    def __init__(self):
        self.capacity: int = 10  # asansör kapasitesi
        self.enter_interval: float = 0.5  # giriş sıklığı

        # giren kişi sayısı aralığı
        self.number_of_people_to_enter: list = [1, 10]

        # çıkış sıklığı
        self.exit_interval: float = 1

        # çıkan kişi sayısı aralığı
        self.number_of_people_to_exit: list = [1, 5]

        self.elevator_interval: float = 0.2  # asansör kat çıkma süresi
        self.is_running: bool = True  # program durumu, false olunca tüm threadler duruyor
        self.customers: list = []  # musterileri dict olarak tutan liste
        self.elevators: list = []  # asansorleri dict olarak tutan liste

        # müşteri listesinde son arayüz güncellemesinden beri değişme var mı
        self.didCustomersListChange: bool = True

        # asansör listesinde son arayüz güncellemesinden beri değişme var mı
        self.didElevatorListChange: bool = True

        # asansör dictlerini yaratıp listeye ekleyen fonksiyonu çağırıyor
        self.create_elevators()

        self.window = tk.Tk(className="Asansor")  # arayüz penceresini oluşturuyor

        # arayüzde kapama tuşuna basınca çağırılacak fonksiyonu tanımlıyor
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        # arayüzdeki katların sıralarını barındıran labelların listelerini tutan liste
        self.floor_labels: list = []

        # arayüzdeki asansörlerin sıralarını barındıran labelların listelerini tutan liste
        self.elevator_labels: list = []

        self.create_labels()  # arayüzdeki tüm labelları yaratıp listelere ekleyen fonksiyon

        # avmye giriş yaptıran threadi başlat
        threading.Thread(target=self.enter_thread).start()

        threading.Thread(target=self.elevator_thread, args=(
            self.elevators[0],)).start()  # 1. asansörün threadini yaratıp başlat

        # avmden çıkış yaptıran threadi başlat
        threading.Thread(target=self.exit_thread).start()

        # kontrol threadini başlat
        threading.Thread(target=self.controller_thread).start()

        self.window.mainloop()  # arayüz event listenerını başlat

    # arayüzde çarpı tuşuna basınca bu fonksiyon çağırılıyor
    def on_close(self) -> None:
        self.is_running = False
        threading.Thread(target=self.destroy).start()

    # bu fonksiyon çağırılınca 0.25 saniye bekleyip pencereyi kapatıyor,
    # çakışmaması için bu da threadle çağırılıyor, yoksa program açık kalıyor
    def destroy(self) -> None:
        time.sleep(0.25)
        self.window.quit()

    # 5 tane asansör dicti yaratıp listeye ekleyen fonksiyon
    def create_elevators(self) -> None:
        for i in range(5):
            self.elevators.append({
                "is_active": True if i == 0 else False,
                "is_running": True if i == 0 else False,
                "floor": 0,
                "direction": "up",
                "capacity": self.capacity,
                "customers": []
            })

    # arayüzdeki labelları yaratan fonksiyon
    def create_labels(self) -> None:
        for index, text in enumerate(["Kat", "Toplam", "Kuyrukta", "Sabit", "0'a Gidecek", "1'e Gidecek", "2'ye Gidecek", "3'e Gidecek", "4'e Gidecek"]):
            tk.Label(text=text, borderwidth=1, relief="solid",
                     width="12").grid(row=0, column=index+1)

        for i in range(5):
            floor = []
            for j in range(9):
                label = tk.Label(text=str(i) if j == 0 else "",
                                 borderwidth=1, width="12", relief="solid")
                label.grid(row=i+1, column=j+1)
                floor.append(label)
            self.floor_labels.append(floor)

        tk.Label("").grid(row=6, column=1)
        tk.Label("").grid(row=7, column=1)

        for index, text in enumerate(["Asansor No", "Durum", "Kapasite", "Iceride", "Konum", "Yon", "0'a Giden", "1'e Giden", "2'ye Giden", "3'e Giden", "4'e Giden"]):
            tk.Label(text=text, borderwidth=1, relief="solid",
                     width="12").grid(row=8, column=index)

        for i in range(5):
            elevator = []
            for j in range(11):
                label = tk.Label(text=str(i+1) if j == 0 else "",
                                 borderwidth=1, width="12", relief="solid")
                label.grid(row=i+9, column=j)
                elevator.append(label)
            self.elevator_labels.append(elevator)

        tk.Label("").grid(row=14, column=1)

    # her 0.5 saniyede bir 1'den 10'a random sayıda yeni müşteri ekleyen fonksiyon
    def enter_thread(self) -> None:
        while self.is_running:
            for _ in range(random.randint(self.number_of_people_to_enter[0], self.number_of_people_to_enter[1])):
                self.customers.append({
                    "current_floor": 0,
                    "target_floor": random.randint(1, 4)
                })
            self.didCustomersListChange = True
            time.sleep(self.enter_interval)

    # her 1 saniyede bir 1'den 5'e random sayıda müşteriyi çıkış sırasına koyan fonksiyon
    def exit_thread(self) -> None:
        while self.is_running:
            for _ in range(random.randint(self.number_of_people_to_exit[0], self.number_of_people_to_exit[1])):
                not_in_queue = [
                    customer for customer in self.customers if customer["target_floor"] is None]
                if len(not_in_queue) != 0:
                    not_in_queue[random.randint(
                        0, len(not_in_queue)-1)]["target_floor"] = 0
            self.didCustomersListChange = True
            time.sleep(self.exit_interval)

    # bir asansör dictini argüman olarak alıp, o asansör işlemlerini yapan fonksiyon
    def elevator_thread(self, elevator: dict) -> None:
        while self.is_running:
            for customer in [c for c in elevator["customers"] if c["target_floor"] == elevator["floor"]]:
                elevator["customers"].remove(customer)
                if elevator["floor"] != 0:
                    customer["current_floor"] = elevator["floor"]
                    customer["target_floor"] = None
                    self.customers.append(customer)

            # şimdi bu katta inen müşteriler indiğine göre içeride müşteri kalmış mı diye bakalım
            if len(elevator["customers"]) == 0:
                if not elevator["is_active"]:
                    elevator["is_running"] = False
                    break
                if elevator["direction"] == "up" and elevator["floor"] != 0:
                    if len([c for c in self.customers if c["current_floor"] > elevator["floor"] and c["target_floor"] is not None]) == 0:
                        elevator["direction"] = "down"

            if elevator["direction"] == "up" and elevator["floor"] == 4:
                elevator["direction"] = "down"

            if elevator["direction"] == "down" and elevator["floor"] == 0:
                elevator["direction"] = "up"

            if (elevator["direction"] == "up" and elevator["floor"] == 0) or (elevator["direction"] == "down" and elevator["floor"] > 0):
                while len(elevator["customers"]) < 10:
                    in_queue = [c for c in self.customers if c["current_floor"]
                                == elevator["floor"] and c["target_floor"] is not None]
                    if len(in_queue) == 0:
                        break
                    in_queue[0]["current_floor"] = None
                    self.customers.remove(in_queue[0])
                    elevator["customers"].append(in_queue[0])

            self.didCustomersListChange = True
            self.didElevatorListChange = True
            time.sleep(self.elevator_interval)

            if elevator["direction"] == "up":
                elevator["floor"] += 1
            else:
                elevator["floor"] -= 1

    # bu fonksiyon çağırılınca arayüzdeki değerlerden değişiklik olanları güncelliyor
    def update_gui(self) -> None:
        if self.didCustomersListChange:
            for i, row in enumerate(self.floor_labels):
                new_texts = [str(i)]
                total = [c for c in self.customers if c["current_floor"] == i]
                in_queue = [c for c in total if c["target_floor"] is not None]
                new_texts.append(str(len(total)))
                new_texts.append(str(len(in_queue)))
                new_texts.append(str(len(total)-len(in_queue)))
                for j in range(5):
                    new_texts.append(
                        str(len([c for c in total if c["target_floor"] == j])))

                for j, label in enumerate(row):
                    if label["text"] != new_texts[j]:
                        label["text"] = new_texts[j]

        if self.didElevatorListChange:
            for i, row in enumerate(self.elevator_labels):
                el = self.elevators[i]
                new_texts = [str(i+1)]
                total = [c for c in el["customers"]]
                new_texts.append(
                    "Calisiyor" if el["is_active"] and el["is_running"] else "Duracak" if el["is_running"] else "Duruyor")
                new_texts.append(str(el["capacity"]))
                new_texts.append(str(len(total)))
                new_texts.append(str(el["floor"]))
                new_texts.append(
                    "Yukari" if el["direction"] == "up" else "Asagi")
                for j in range(5):
                    new_texts.append(
                        str(len([c for c in total if c["target_floor"] == j])))

                for j, label in enumerate(row):
                    if label["text"] != new_texts[j]:
                        label["text"] = new_texts[j]

        self.didElevatorListChange = False
        self.didCustomersListChange = False
        self.window.update()

    def controller_thread(self) -> None:
        while self.is_running:
            self.update_gui()
            active = [e for e in self.elevators if e["is_active"]]
            inactive = [e for e in self.elevators if not e["is_active"]]
            in_queue = len(
                [c for c in self.customers if c["target_floor"] is not None])
            capacity = sum([e["capacity"] for e in active])
            if len(active) > 1:
                if capacity >= in_queue:
                    active[-1]["is_active"] = False

            if in_queue >= capacity*2:
                if len(inactive) > 0:
                    if inactive[0]["is_running"]:
                        inactive[0]["is_active"] = True
                    else:
                        inactive[0]["is_active"] = True
                        threading.Thread(
                            target=self.elevator_thread, args=(inactive[0],)).start()
                        inactive[0]["is_running"] = True

            time.sleep(0.02)


if __name__ == "__main__":
    #Mall()
    def func(a):
        return a[0]*a[1]

    liste=[[5,6],[1,19],[7,8]]
    liste.sort(key=func)
    print(liste)
