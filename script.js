document.addEventListener('DOMContentLoaded', () => {
    const searchButton = document.getElementById('search-button');
    const turnOnButton = document.getElementById('turn-on');
    const turnOffButton = document.getElementById('turn-off');
    const changeChannelButton = document.getElementById('change-channel');
    const tvList = document.getElementById('tv-list');
    const status = document.getElementById('status');

    let selectedTVIp = '';

    searchButton.addEventListener('click', async () => {
        // Simulação de busca de TVs na rede
        const devices = await fetch('/api/get_devices').then(response => response.json());
        tvList.innerHTML = '';
        devices.forEach(device => {
            if (device.type === 'TV') {
                const li = document.createElement('li');
                li.textContent = `IP: ${device.ip} | MAC: ${device.mac}`;
                li.addEventListener('click', () => {
                    selectedTVIp = device.ip;
                    status.textContent = `Conectado à TV com IP: ${selectedTVIp}`;
                });
                tvList.appendChild(li);
            }
        });
    });

    turnOnButton.addEventListener('click', () => {
        if (!selectedTVIp) {
            status.textContent = 'Por favor, conecte-se a uma TV primeiro.';
            return;
        }
        fetch(`http://${selectedTVIp}:8060/keypress/PowerOn`, { method: 'POST' })
            .then(response => {
                if (response.ok) {
                    status.textContent = 'TV ligada com sucesso.';
                } else {
                    status.textContent = `Falha ao ligar a TV. Código de status: ${response.status}`;
                }
            })
            .catch(error => status.textContent = `Erro ao tentar ligar a TV: ${error}`);
    });

    turnOffButton.addEventListener('click', () => {
        if (!selectedTVIp) {
            status.textContent = 'Por favor, conecte-se a uma TV primeiro.';
            return;
        }
        fetch(`http://${selectedTVIp}:8060/keypress/PowerOff`, { method: 'POST' })
            .then(response => {
                if (response.ok) {
                    status.textContent = 'TV desligada com sucesso.';
                } else {
                    status.textContent = `Falha ao desligar a TV. Código de status: ${response.status}`;
                }
            })
            .catch(error => status.textContent = `Erro ao tentar desligar a TV: ${error}`);
    });

    changeChannelButton.addEventListener('click', () => {
        if (!selectedTVIp) {
            status.textContent = 'Por favor, conecte-se a uma TV primeiro.';
            return;
        }
        const channel = prompt('Digite o número do canal:');
        if (channel) {
            fetch(`http://${selectedTVIp}:8060/keypress/ChannelUp`, { method: 'POST' })
                .then(response => {
                    if (response.ok) {
                        status.textContent = `Canal alterado para ${channel}.`;
                    } else {
                        status.textContent = `Falha ao mudar o canal. Código de status: ${response.status}`;
                    }
                })
                .catch(error => status.textContent = `Erro ao tentar mudar o canal: ${error}`);
        }
    });
});
