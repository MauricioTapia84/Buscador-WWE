/**
 * ⚛️ AGENTNOVA WEB HUB - LÓGICA DE APLICACIÓN
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const modelSelect = document.getElementById('model-select');
  const agentModelSelect = document.getElementById('agent-model-select');
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input');
  const messagesContainer = document.getElementById('messages-container');
  const welcomeScreen = document.getElementById('welcome-screen');
  const newChatBtn = document.getElementById('new-chat-btn');
  const chatList = document.getElementById('chat-list');
  const statusDot = document.getElementById('ollama-status-dot');
  const statusText = document.getElementById('ollama-status-text');
  
  // Settings dialog elements
  const settingsToggleBtn = document.getElementById('settings-toggle-btn');
  const settingsDialog = document.getElementById('settings-dialog');
  const ollamaUrlInput = document.getElementById('ollama-url-input');
  const testConnectionBtn = document.getElementById('test-connection-btn');
  const closeDialogBtn = document.querySelector('.close-dialog-btn');

  // Image attachment elements
  const imageUpload = document.getElementById('image-upload');
  const attachBtn = document.getElementById('attach-btn');
  const imagePreviewContainer = document.getElementById('image-preview-container');
  const imagePreview = document.getElementById('image-preview');
  const removeImageBtn = document.getElementById('remove-image-btn');

  // AgentNova popover elements
  const showAgentPanelBtn = document.getElementById('show-agent-panel-btn');
  const agentPanel = document.getElementById('agent-panel');
  const agentGoal = document.getElementById('agent-goal');
  const generateCommandBtn = document.getElementById('generate-command-btn');
  const commandOutputBox = document.getElementById('command-output-box');
  const generatedCommand = document.getElementById('generated-command');
  const copyCommandBtn = document.getElementById('copy-command-btn');

  // Application State
  let conversations = JSON.parse(localStorage.getItem('agentnova_conversations') || '[]');
  let activeConversationId = localStorage.getItem('agentnova_active_conversation_id') || null;
  let settings = JSON.parse(localStorage.getItem('agentnova_settings') || '{"ollamaUrl": "http://localhost:11434"}');
  let models = [];
  let attachedImageBase64 = null;
  let systemPromptContent = "";
  let skillsContent = "";

  const workspaceMetadata = `
CONTEXTO DEL ESPACIO DE TRABAJO (WORKSPACE):
- Ruta absoluta del proyecto: /home/mauricio/Documentos/GitHub/Ciencia-Datos
- Estructura y directorios clave del proyecto:
  ├── agent/                  # Componentes y código del agente autónomo
  │   ├── config/             # Configuración del agente (modelos, prompts)
  │   │   ├── prompts/
  │   │   │   └── system_prompt.txt
  │   │   └── models.yaml
  │   ├── skills/             # Habilidades/herramientas personalizadas del agente
  │   │   ├── data-skills/
  │   │   │   └── SKILL.md     # Documentación de data-skills
  │   │   └── data_skills.py  # Código Python para análisis y ejecución de notebooks
  │   ├── web/                # Interfaz web local (la que estás usando ahora mismo)
  │   │   ├── index.html
  │   │   ├── style.css
  │   │   └── app.js
  │   └── run_agent.py        # Ejecutor CLI del agente autónomo
  ├── scripts/                # Scripts de automatización y control
  │   ├── setup.sh            # Inicialización del entorno, dependencias y Ollama
  │   ├── start-agent.sh      # Lanzador del agente en consola
  │   └── start-web-ui.sh     # Servidor web local
  ├── knowledge/              # Carpeta para almacenamiento de bases de conocimiento
  ├── src/                    # Código de ciencia de datos del usuario
  ├── requirements.txt        # Dependencias de Python necesarias
  └── MANUAL_DE_USO.md        # Manual de usuario y guías
`;

  // Apply saved URL to input
  ollamaUrlInput.value = settings.ollamaUrl;

  // Initialize
  initApp();

  async function loadPrompts() {
    try {
      const promptRes = await fetch('/agent/config/prompts/system_prompt.txt');
      if (promptRes.ok) {
        systemPromptContent = await promptRes.text();
      }
    } catch (e) {
      console.warn('No se pudo cargar el system prompt:', e);
    }
    try {
      const skillRes = await fetch('/agent/skills/data-skills/SKILL.md');
      if (skillRes.ok) {
        skillsContent = await skillRes.text();
      }
    } catch (e) {
      console.warn('No se pudo cargar el archivo SKILL.md:', e);
    }
  }

  async function initApp() {
    checkOllamaStatus();
    renderChatHistory();
    if (activeConversationId) {
      loadConversation(activeConversationId);
    }
    
    // Cargar prompts y contexto del workspace
    await loadPrompts();
    
    // Auto-resize textarea
    chatInput.addEventListener('input', () => {
      chatInput.style.height = 'auto';
      chatInput.style.height = `${chatInput.scrollHeight}px`;
    });

    // Image Upload Events
    attachBtn.addEventListener('click', () => imageUpload.click());

    imageUpload.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
          attachedImageBase64 = event.target.result;
          imagePreview.src = attachedImageBase64;
          imagePreviewContainer.style.display = 'flex';
        };
        reader.readAsDataURL(file);
      }
    });

    removeImageBtn.addEventListener('click', () => {
      imageUpload.value = '';
      attachedImageBase64 = null;
      imagePreviewContainer.style.display = 'none';
      imagePreview.src = '';
    });
  }

  // Check Ollama Service Connectivity
  async function checkOllamaStatus() {
    try {
      const response = await fetch(`${settings.ollamaUrl}/api/tags`, { method: 'GET' });
      if (response.ok) {
        const data = await response.json();
        models = data.models || [];
        
        statusDot.className = 'status-dot online';
        statusText.textContent = 'Ollama Conectado';
        
        populateModelSelectors();
      } else {
        throw new Error('Servidor respondió con error');
      }
    } catch (error) {
      statusDot.className = 'status-dot offline';
      statusText.textContent = 'Ollama Desconectado';
      modelSelect.innerHTML = '<option value="">Error al cargar modelos</option>';
      console.error('Error de conexión a Ollama:', error);
    }
  }

  const modelLegend = document.getElementById('model-legend');

  function updateModelLegend(modelName) {
    if (!modelLegend) return;
    const name = modelName.toLowerCase();
    if (name.includes('qwen2.5-coder')) {
      if (name.includes('1.5b') || name.includes('3b')) {
        modelLegend.textContent = "💡 Qwen Coder (Ligero): Programación rápida, óptimo para equipos con poca RAM/GPU.";
      } else {
        modelLegend.textContent = "💡 Qwen Coder (7B): Excelente para desarrollo de software y análisis de datos complejo.";
      }
    } else if (name.includes('llama3.2')) {
      if (name.includes('vision') || name.includes('11b')) {
        modelLegend.textContent = "💡 Llama 3.2 Vision: Óptimo para chat y análisis de imágenes locales.";
      } else {
        modelLegend.textContent = "💡 Llama 3.2 (3B): Muy rápido y fluido. Ideal para consultas teóricas y estudio.";
      }
    } else if (name.includes('llava')) {
      modelLegend.textContent = "💡 Llava: Especializado en visión y comprensión de imágenes locales.";
    } else {
      modelLegend.textContent = "💡 Modelo local: Listo para consultas generales.";
    }
  }

  // Populate model dropdown elements
  function populateModelSelectors() {
    if (models.length === 0) {
      modelSelect.innerHTML = '<option value="">No hay modelos instalados</option>';
      return;
    }

    const savedModel = localStorage.getItem('agentnova_selected_model') || '';
    
    let optionsHtml = '';
    models.forEach(model => {
      const isSelected = model.name === savedModel || (savedModel === '' && model.name.includes('qwen2.5-coder'));
      optionsHtml += `<option value="${model.name}" ${isSelected ? 'selected' : ''}>${model.name}</option>`;
    });

    modelSelect.innerHTML = optionsHtml;

    // Actualizar leyenda inicial
    const initialModel = modelSelect.value || (models.length > 0 ? models[0].name : '');
    updateModelLegend(initialModel);
    
    // Al cambiar de modelo principal, guardar elección y actualizar leyenda
    modelSelect.addEventListener('change', (e) => {
      localStorage.setItem('agentnova_selected_model', e.target.value);
      updateModelLegend(e.target.value);
    });

    // Rellenar selector del agente
    let agentOptionsHtml = '';
    models.forEach(model => {
      const isSelected = model.name.includes('qwen2.5-coder') || model.name.includes('llama3.2');
      agentOptionsHtml += `<option value="${model.name}" ${isSelected ? 'selected' : ''}>${model.name}</option>`;
    });
    agentModelSelect.innerHTML = agentOptionsHtml;
  }

  // Settings Modal controls
  settingsToggleBtn.addEventListener('click', () => {
    settingsDialog.showModal();
  });

  closeDialogBtn.addEventListener('click', () => {
    settingsDialog.close();
  });

  settingsDialog.addEventListener('submit', (e) => {
    settings.ollamaUrl = ollamaUrlInput.value.replace(/\/$/, '');
    localStorage.setItem('agentnova_settings', JSON.stringify(settings));
    checkOllamaStatus();
  });

  testConnectionBtn.addEventListener('click', async () => {
    const tempUrl = ollamaUrlInput.value.replace(/\/$/, '');
    testConnectionBtn.textContent = 'Probando...';
    testConnectionBtn.disabled = true;
    try {
      const response = await fetch(`${tempUrl}/api/tags`);
      if (response.ok) {
        alert('¡Conexión exitosa con Ollama!');
      } else {
        alert('Error: El servidor respondió pero no de forma esperada.');
      }
    } catch (err) {
      alert(`No se pudo conectar a Ollama en ${tempUrl}. Asegúrate de que el servicio esté activo y no esté bloqueado por CORS.`);
    } finally {
      testConnectionBtn.textContent = 'Probar Conexión';
      testConnectionBtn.disabled = false;
    }
  });

  // Agent Panel Show / Hide (Right Sliding Sidebar)
  const closePanelBtn = document.getElementById('close-panel-btn');

  showAgentPanelBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    agentPanel.classList.add('open');
  });

  closePanelBtn.addEventListener('click', () => {
    agentPanel.classList.remove('open');
  });

  // Cerrar el panel si se hace clic fuera de él
  document.addEventListener('click', (e) => {
    if (!agentPanel.contains(e.target) && e.target !== showAgentPanelBtn) {
      agentPanel.classList.remove('open');
    }
  });

  // Generate IA Oruga agent command
  generateCommandBtn.addEventListener('click', () => {
    const goal = agentGoal.value.trim();
    if (!goal) {
      alert('Por favor escribe un objetivo para el agente.');
      return;
    }
    const model = agentModelSelect.value;
    
    // Command format for the new start-oruga.sh script
    generatedCommand.textContent = `./start-oruga.sh --model "${model}" --goal "${goal.replace(/"/g, '\\"')}"`;

    commandOutputBox.style.display = 'flex';
  });

  // Copy command to clipboard
  copyCommandBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(generatedCommand.textContent);
    copyCommandBtn.textContent = 'Copiado!';
    setTimeout(() => {
      copyCommandBtn.textContent = 'Copiar';
    }, 2000);
  });

  // Chat History Management
  newChatBtn.addEventListener('click', startNewChat);

  function startNewChat() {
    activeConversationId = null;
    localStorage.removeItem('agentnova_active_conversation_id');
    
    // Clear chat layout
    messagesContainer.innerHTML = '';
    messagesContainer.appendChild(welcomeScreen);
    welcomeScreen.style.display = 'flex';
    
    // Deselect sidebar active
    document.querySelectorAll('.chat-item').forEach(item => item.classList.remove('active'));
  }

  function renderChatHistory() {
    if (conversations.length === 0) {
      chatList.innerHTML = '<div class="dialog-info" style="padding: 10px;">No hay chats recientes</div>';
      return;
    }

    let historyHtml = '';
    conversations.forEach(chat => {
      const isActive = chat.id === activeConversationId;
      historyHtml += `
        <div class="chat-item ${isActive ? 'active' : ''}" data-id="${chat.id}">
          <span class="chat-item-title">${escapeHtml(chat.title)}</span>
          <span class="delete-chat-btn" data-id="${chat.id}">×</span>
        </div>
      `;
    });
    chatList.innerHTML = historyHtml;

    // Add click listeners
    document.querySelectorAll('.chat-item').forEach(item => {
      item.addEventListener('click', (e) => {
        if (e.target.classList.contains('delete-chat-btn')) {
          e.stopPropagation();
          deleteConversation(e.target.dataset.id);
        } else {
          loadConversation(item.dataset.id);
        }
      });
    });
  }

  function loadConversation(id) {
    activeConversationId = id;
    localStorage.setItem('agentnova_active_conversation_id', id);
    
    const conversation = conversations.find(c => c.id === id);
    if (!conversation) {
      startNewChat();
      return;
    }

    renderChatHistory();

    // Render messages
    welcomeScreen.style.display = 'none';
    messagesContainer.innerHTML = '';
    
    conversation.messages.forEach(msg => {
      appendMessage(msg.role, msg.content, false, msg.image);
    });

    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function deleteConversation(id) {
    conversations = conversations.filter(c => c.id !== id);
    localStorage.setItem('agentnova_conversations', JSON.stringify(conversations));
    
    if (activeConversationId === id) {
      startNewChat();
    } else {
      renderChatHistory();
    }
  }

  // Save conversation helper
  function saveCurrentConversation(messages) {
    if (!activeConversationId) {
      // Create new conversation
      const firstUserMsg = messages.find(m => m.role === 'user');
      const title = firstUserMsg ? firstUserMsg.content.substring(0, 30) + (firstUserMsg.content.length > 30 ? '...' : '') : 'Nuevo Chat';
      activeConversationId = 'conv_' + Date.now();
      localStorage.setItem('agentnova_active_conversation_id', activeConversationId);
      
      conversations.unshift({
        id: activeConversationId,
        title: title,
        messages: messages
      });
    } else {
      // Update existing conversation
      const convIndex = conversations.findIndex(c => c.id === activeConversationId);
      if (convIndex !== -1) {
        conversations[convIndex].messages = messages;
      }
    }
    
    localStorage.setItem('agentnova_conversations', JSON.stringify(conversations));
    renderChatHistory();
  }

  // HTML escape helper
  function escapeHtml(unsafe) {
    return unsafe
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Premium Markdown and Diff Renderer
  function parseMarkdown(text) {
    if (!text) return "";
    
    // Extract code blocks to avoid formatting markdown inside code
    const codeBlocks = [];
    let processedText = text.replace(/```(\w*)\n([\s\S]*?)```/g, (match, lang, code) => {
      const id = `___CODE_BLOCK_${codeBlocks.length}___`;
      const escapedCode = escapeHtml(code.trim());
      
      // Highlight diff lines inside code blocks
      let formattedCode = escapedCode;
      formattedCode = escapedCode.split('\n').map(line => {
        if (line.startsWith('+ ') || line.startsWith('+')) {
          return `<span class="diff-line-added">${line}</span>`;
        } else if (line.startsWith('- ') || line.startsWith('-')) {
          return `<span class="diff-line-removed">${line}</span>`;
        }
        return line;
      }).join('\n');

      // Safe base64 conversion to avoid escaping quotes in button click handler
      const base64Code = btoa(unescape(encodeURIComponent(code.trim())));

      // Render appropriate buttons depending on language
      let runBtnHtml = "";
      const lowerLang = (lang || '').toLowerCase();
      if (lowerLang === 'bash' || lowerLang === 'sh' || lowerLang === 'shell' || lowerLang === 'cmd') {
        runBtnHtml = `<button class="code-run-btn" style="background: none; border: none; color: var(--accent-purple); cursor: pointer; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.7rem; font-weight: 500; margin-left: 0.5rem; border: 1px solid var(--border-glow); transition: var(--transition-smooth);" onclick="window.executeLocalCommand('${base64Code}', this)">Ejecutar</button>`;
      } else if (lowerLang === 'diff') {
        runBtnHtml = `<button class="code-run-btn" style="background: none; border: none; color: var(--accent-purple); cursor: pointer; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.7rem; font-weight: 500; margin-left: 0.5rem; border: 1px solid var(--border-glow); transition: var(--transition-smooth);" onclick="window.applyLocalDiff('${base64Code}', this)">Aplicar Parche</button>`;
      } else if (lowerLang === 'toml' || lowerLang === 'yaml' || lowerLang === 'json' || lowerLang === 'python' || lowerLang === 'py' || lowerLang === 'text' || lowerLang === 'md' || lowerLang === 'markdown') {
        runBtnHtml = `<button class="code-run-btn" style="background: none; border: none; color: var(--accent-purple); cursor: pointer; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.7rem; font-weight: 500; margin-left: 0.5rem; border: 1px solid var(--border-glow); transition: var(--transition-smooth);" onclick="window.saveLocalFile('${base64Code}', this)">Guardar Archivo</button>`;
      }

      const blockHtml = `
        <div class="code-block-container">
          <div class="code-block-header">
            <span class="code-lang">${lang || 'código'}</span>
            <div>
              <button class="code-copy-btn" onclick="const code = decodeURIComponent(escape(atob('${base64Code}'))); navigator.clipboard.writeText(code); this.textContent = '¡Copiado!'; setTimeout(() => this.textContent = 'Copiar', 2000)">Copiar</button>
              ${runBtnHtml}
            </div>
          </div>
          <pre><code class="language-${lang || ''}">${formattedCode}</code></pre>
        </div>
      `;
      codeBlocks.push(blockHtml);
      return id;
    });

    // Escape HTML of other text
    processedText = escapeHtml(processedText);

    // Headers
    processedText = processedText.replace(/^#### (.*?)$/gm, '<h4>$1</h4>');
    processedText = processedText.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
    processedText = processedText.replace(/^## (.*?)$/gm, '<h2>$1</h2>');
    processedText = processedText.replace(/^# (.*?)$/gm, '<h1>$1</h1>');

    // Bold
    processedText = processedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Inline code
    processedText = processedText.replace(/`(.*?)`/g, '<code>$1</code>');

    // Diffs inside regular markdown lines (for bullet point lists showing changes)
    processedText = processedText.split('\n').map(line => {
      if (line.startsWith('+ ') || line.startsWith('+')) {
        return `<span class="diff-line-added">${line}</span>`;
      } else if (line.startsWith('- ') || line.startsWith('-')) {
        return `<span class="diff-line-removed">${line}</span>`;
      }
      return line;
    }).join('\n');

    // Bullet points
    processedText = processedText.replace(/^\s*[-*]\s+(.*?)$/gm, '<li>$1</li>');
    
    // Line breaks
    processedText = processedText.replace(/\n/g, '<br>');

    // Re-insert code blocks
    codeBlocks.forEach((block, index) => {
      processedText = processedText.replace(`___CODE_BLOCK_${index}___`, block);
    });

    return processedText;
  }

  // UI Message insertion
  function appendMessage(role, content, animate = true, imageBase64 = null) {
    // Hide welcome screen if showing
    welcomeScreen.style.display = 'none';

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? 'U' : 'AI';

    const body = document.createElement('div');
    body.className = 'message-content';

    // Renders attached image if present
    if (imageBase64) {
      const imgContainer = document.createElement('div');
      imgContainer.className = 'message-image-container';
      const img = document.createElement('img');
      img.src = imageBase64;
      img.className = 'message-image';
      img.alt = 'Imagen adjuntada';
      imgContainer.appendChild(img);
      body.appendChild(imgContainer);
    }

    const textSpan = document.createElement('span');
    textSpan.innerHTML = parseMarkdown(content);
    body.appendChild(textSpan);

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(body);
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    return textSpan;
  }

  // Handle Form Submission
  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const prompt = chatInput.value.trim();
    if (!prompt && !attachedImageBase64) return;

    // Save attached image reference and clear preview
    const currentAttachedImage = attachedImageBase64;
    if (currentAttachedImage) {
      removeImageBtn.click();
    }

    // Clear input
    chatInput.value = '';
    chatInput.style.height = 'auto';

    // Get current conversation messages
    let activeConversation = conversations.find(c => c.id === activeConversationId);
    let messages = activeConversation ? [...activeConversation.messages] : [];

    // Add user message to state and UI
    const newUserMessage = { role: 'user', content: prompt };
    if (currentAttachedImage) {
      newUserMessage.image = currentAttachedImage;
    }
    messages.push(newUserMessage);
    appendMessage('user', prompt, true, currentAttachedImage);

    // Save state
    saveCurrentConversation(messages);

    // Add placeholder assistant bubble with loading/typing text
    const assistantBody = appendMessage('assistant', '...', true);
    
    // Default fallback thinking tasks
    let taskList = [
      "Analizar la consulta del usuario",
      "Escanear contexto del espacio de trabajo",
      "Validar comandos y habilidades del agente",
      "Generar respuesta técnica detallada"
    ];

    // Helper to render tasks list HTML
    function renderThinkingSteps(tasks, activeIndex) {
      let html = '<div class="thinking-steps-container">';
      html += '<div style="font-weight: bold; font-size: 0.85rem; color: var(--accent-cyan); margin-bottom: 0.4rem; display: flex; align-items: center; gap: 0.4rem;">🐛 <span>Subtareas de IA Oruga:</span></div>';
      tasks.forEach((task, i) => {
        let statusIcon = "⏳";
        let statusClass = "pending";
        if (i < activeIndex) {
          statusIcon = "✅";
          statusClass = "completed";
        } else if (i === activeIndex) {
          statusIcon = "⚙️";
          statusClass = "active";
        }
        html += `<div class="thinking-step-item ${statusClass}">${statusIcon} <span>${task}</span></div>`;
      });
      html += '</div>';
      return html;
    }

    // Selected Model
    const model = modelSelect.value;
    if (!model) {
      assistantBody.innerHTML = 'Error: Selecciona un modelo de Ollama válido.';
      return;
    }

    // 1. DYNAMIC PRE-FLIGHT TASK PLANNER (Split request into subtasks using Ollama)
    assistantBody.innerHTML = renderThinkingSteps(["Dividiendo solicitud en subtareas..."], 0);

    try {
      // Build pre-flight message history to provide full conversation context to the task planner
      const preflightMessages = [
        {
          role: 'system',
          content: 'Basándote en el historial de la conversación y el último mensaje, divide la solicitud actual en exactamente 3 o 4 tareas técnicas secuenciales muy breves y concretas. Responde ÚNICAMENTE con una lista JSON de strings, sin markdown ni explicaciones. Ejemplo: ["Analizar archivos obsoletos", "Mover scripts a temp_obsolete_backup", "Actualizar README.md"].'
        },
        ...messages.map(msg => ({ role: msg.role, content: msg.content }))
      ];

      const preflightResponse = await fetch(`${settings.ollamaUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: model,
          messages: preflightMessages,
          stream: false
        })
      });
      if (preflightResponse.ok) {
        const preflightResult = await preflightResponse.json();
        const jsonText = preflightResult.message?.content.trim();
        const match = jsonText.match(/\[\s*".*?"\s*\]/s) || jsonText.match(/\[[\s\S]*?\]/);
        if (match) {
          taskList = JSON.parse(match[0]);
        }
      }
    } catch (err) {
      console.warn('Pre-flight task planner failed, fallback to defaults:', err);
      if (prompt.toLowerCase().includes('limpiar') || prompt.toLowerCase().includes('ordenar')) {
        taskList = [
          "Identificar scripts obsoletos (start-agent.sh/start-web-ui.sh)",
          "Crear carpeta temporal temp_obsolete_backup/",
          "Preparar comandos seguros de migración",
          "Actualizar documentación e indicar cambios incrementales"
        ];
      }
    }

    // Start rendering steps progress
    let activeStep = 0;
    assistantBody.innerHTML = renderThinkingSteps(taskList, activeStep);
    
    const stepInterval = setInterval(() => {
      if (activeStep < taskList.length - 1) {
        activeStep++;
        assistantBody.innerHTML = renderThinkingSteps(taskList, activeStep);
      }
    }, 2800);

    // Prepare API messages history payload format
    const apiPayloadMessages = [];

    // Prepend system prompt + skills + workspace metadata as system instruction
    let systemContext = "";
    if (systemPromptContent) {
      systemContext += `INSTRUCCIONES DEL SISTEMA:\n${systemPromptContent.trim()}\n\n`;
    }
    if (skillsContent) {
      systemContext += `DOCUMENTACIÓN DE SKILLS/HERRAMIENTAS DISPONIBLES:\n${skillsContent.trim()}\n\n`;
    }
    systemContext += `INFORMACIÓN DEL ESPACIO DE TRABAJO (WORKSPACE LOCAL):\n${workspaceMetadata.trim()}\n\n`;
    
    // Reglas de seguridad críticas para evitar borrado/sobrescritura destructivos
    systemContext += `REGLAS DE SEGURIDAD CRÍTICAS (DEBES SEGUIRLAS ESTRICTAMENTE):\n`;
    systemContext += `- NUNCA sugieras borrar o limpiar archivos usando comandos de terminal ciegos como 'find . -delete' o 'rm' en masa sin indicarle al usuario que lo verifique primero archivo por archivo.\n`;
    systemContext += `- NUNCA sugieras sobrescribir archivos completos de documentación (como README.md o MANUAL_DE_USO.md) con esqueletos de pocas líneas. Siempre sugiere ediciones incrementales o indica la sección exacta a modificar para no borrar el contenido existente.\n`;
    systemContext += `- NUNCA inventes archivos en el repositorio. Si necesitas saber si existe un archivo, pide al usuario verificarlo.\n`;
    systemContext += `- Si el usuario te pide limpiar el repositorio, sugiérele mover archivos a una carpeta temporal (por ejemplo, 'temp_backup/') en lugar de eliminarlos permanentemente.\n\n`;
    
    systemContext += `Utiliza este contexto para guiar al usuario. Si te preguntan por habilidades, describe cómo llamarlas en la CLI local o cómo ejecutarlas. Si te preguntan dónde está alojado el proyecto o qué archivos/carpetas contiene, responde usando la información del workspace.`;

    apiPayloadMessages.push({
      role: 'system',
      content: systemContext
    });

    messages.forEach(msg => {
      const formatted = { role: msg.role, content: msg.content };
      if (msg.image) {
        formatted.images = [msg.image.split(',')[1]]; // remove data:image/png;base64, prefix
      }
      apiPayloadMessages.push(formatted);
    });

    // Connect to Ollama API for main completion
    try {
      const response = await fetch(`${settings.ollamaUrl}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: model,
          messages: apiPayloadMessages,
          stream: false // Non-stream for simple stable rendering
        })
      });

      clearInterval(stepInterval);

      if (!response.ok) {
        throw new Error('Fallo en la petición a Ollama API');
      }

      const result = await response.json();
      const answer = result.message?.content || 'Sin respuesta.';

      // Format response, prepending all completed steps checklist
      const finalStepsHtml = renderThinkingSteps(taskList, taskList.length);
      assistantBody.innerHTML = finalStepsHtml + `<div style="margin-top: 1rem; border-top: 1px solid var(--border-color); padding-top: 1rem;">${parseMarkdown(answer)}</div>`;
      
      // Update state
      messages.push({ role: 'assistant', content: answer });
      saveCurrentConversation(messages);

    } catch (err) {
      clearInterval(stepInterval);
      assistantBody.innerHTML = `<span style="color: hsl(0, 85%, 60%)">Error de conexión con Ollama en ${settings.ollamaUrl}. Asegúrate de que el servicio esté iniciado y responda.</span>`;
      console.error(err);
    }
  });

  // Handle Quick Prompts
  document.querySelectorAll('.quick-prompt-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      chatInput.value = btn.dataset.prompt;
      chatInput.dispatchEvent(new Event('input')); // auto resize
      chatInput.focus();
    });
  });

  // Safe Interactive Execution of Local Commands in the Workspace
  window.executeLocalCommand = async function(base64Code, buttonElement) {
    const rawCommand = decodeURIComponent(escape(atob(base64Code)));
    
    // Clean comments and format commands to execute sequentially
    const cleanLines = rawCommand.split('\n')
      .map(line => line.trim())
      .filter(line => line.length > 0 && !line.startsWith('#'));
      
    const executableCommand = cleanLines.join(' && ');

    if (!executableCommand) {
      alert("No hay comandos ejecutables en este bloque (sólo comentarios).");
      return;
    }

    if (!confirm(`¿Estás seguro de que deseas ejecutar este comando localmente en tu repositorio?\n\nComando:\n${cleanLines.join('\n')}`)) {
      return;
    }

    buttonElement.textContent = "Ejecutando...";
    buttonElement.disabled = true;

    // Find code block container to output stdout/stderr
    const container = buttonElement.closest('.code-block-container');
    let consoleBox = container.querySelector('.console-output-box');
    if (!consoleBox) {
      consoleBox = document.createElement('div');
      consoleBox.className = 'console-output-box';
      consoleBox.style = 'background-color: #0b0f19; border-top: 1px solid var(--border-color); font-family: var(--font-mono); font-size: 0.75rem; padding: 0.75rem; color: #3fb950; max-height: 180px; overflow-y: auto; white-space: pre-wrap; word-break: break-all;';
      container.appendChild(consoleBox);
    }

    consoleBox.textContent = `> ${executableCommand}\n\n`;

    try {
      const response = await fetch('/api/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: executableCommand })
      });

      if (response.ok) {
        const result = await response.json();
        
        if (result.stdout) {
          consoleBox.textContent += result.stdout;
        }
        if (result.stderr) {
          consoleBox.textContent += `[ERROR] ${result.stderr}`;
          consoleBox.style.color = '#ff6b6b';
        }
        
        if (result.code === 0) {
          buttonElement.textContent = "✅ Éxito";
          buttonElement.style.color = "var(--accent-purple)";
        } else {
          buttonElement.textContent = "❌ Fallo";
          buttonElement.style.color = "#ff6b6b";
          consoleBox.textContent += `\n[PROCESO TERMINADO CON CÓDIGO DE ERROR: ${result.code}]\n`;
        }
      } else {
        const errorData = await response.json();
        consoleBox.textContent += `[ERROR BACKEND]: ${errorData.error || 'Fallo de comunicación'}`;
        consoleBox.style.color = '#ff6b6b';
        buttonElement.textContent = "❌ Fallo API";
      }
    } catch (err) {
      console.warn('Execution fetch error:', err);
      consoleBox.textContent += `[ERROR] No se pudo establecer conexión con el servidor backend de ejecución. Asegúrate de haber arrancado la interfaz con "./start-oruga.sh".`;
      consoleBox.style.color = '#ff6b6b';
      buttonElement.textContent = "❌ Error Red";
    } finally {
      buttonElement.disabled = false;
    }
  };

  // Helper to find filenames mentioned in the text before the code block
  function findPrecedingFilename(element) {
    const parent = element.closest('.message-content');
    if (!parent) return "";
    
    const container = element.closest('.code-block-container');
    const allNodes = Array.from(parent.querySelectorAll('.code-block-container, h1, h2, h3, h4, p, li'));
    const containerIdx = allNodes.indexOf(container);
    
    // Scan backwards
    for (let i = containerIdx - 1; i >= 0; i--) {
      const text = allNodes[i].textContent || "";
      // Match typical filenames like netlify.toml, README.md, etc.
      const match = text.match(/[\w\-./\\]+\.(md|txt|py|sh|bat|toml|json|yaml|yml)/i);
      if (match) {
        return match[0].replace(/^[\s#\-*]+/, ''); // Clean prefixes
      }
    }
    return "";
  }

  // Interactive Save File Handler
  window.saveLocalFile = async function(base64Content, buttonElement) {
    const content = decodeURIComponent(escape(atob(base64Content)));
    let defaultPath = findPrecedingFilename(buttonElement);
    
    let filepath = prompt("¿Con qué nombre/ruta deseas guardar este archivo en el repositorio?", defaultPath);
    if (!filepath) return;
    
    buttonElement.textContent = "Guardando...";
    buttonElement.disabled = true;
    
    const container = buttonElement.closest('.code-block-container');
    let consoleBox = container.querySelector('.console-output-box');
    if (!consoleBox) {
      consoleBox = document.createElement('div');
      consoleBox.className = 'console-output-box';
      consoleBox.style = 'background-color: #0b0f19; border-top: 1px solid var(--border-color); font-family: var(--font-mono); font-size: 0.75rem; padding: 0.75rem; color: #3fb950; max-height: 180px; overflow-y: auto; white-space: pre-wrap; word-break: break-all;';
      container.appendChild(consoleBox);
    }
    
    consoleBox.textContent = `> Escribiendo archivo en ${filepath}...\n\n`;
    
    try {
      const response = await fetch('/api/write_file', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filepath, content })
      });
      
      if (response.ok) {
        const result = await response.json();
        consoleBox.textContent += result.message || "Archivo escrito con éxito.";
        buttonElement.textContent = "✅ Guardado";
        buttonElement.style.color = "var(--accent-purple)";
      } else {
        const errorData = await response.json();
        consoleBox.textContent += `[ERROR]: ${errorData.error || 'Fallo de escritura'}`;
        consoleBox.style.color = '#ff6b6b';
        buttonElement.textContent = "❌ Error";
      }
    } catch (err) {
      consoleBox.textContent += `[ERROR]: No se pudo conectar con el servidor local.`;
      consoleBox.style.color = '#ff6b6b';
      buttonElement.textContent = "❌ Error Red";
    } finally {
      buttonElement.disabled = false;
    }
  };

  // Interactive Apply Patch Handler
  window.applyLocalDiff = async function(base64Diff, buttonElement) {
    const diffText = decodeURIComponent(escape(atob(base64Diff)));
    let defaultPath = findPrecedingFilename(buttonElement);
    
    let filepath = prompt("¿A qué archivo del repositorio deseas aplicar este parche diff?", defaultPath);
    if (!filepath) return;
    
    buttonElement.textContent = "Aplicando...";
    buttonElement.disabled = true;
    
    const container = buttonElement.closest('.code-block-container');
    let consoleBox = container.querySelector('.console-output-box');
    if (!consoleBox) {
      consoleBox = document.createElement('div');
      consoleBox.className = 'console-output-box';
      consoleBox.style = 'background-color: #0b0f19; border-top: 1px solid var(--border-color); font-family: var(--font-mono); font-size: 0.75rem; padding: 0.75rem; color: #3fb950; max-height: 180px; overflow-y: auto; white-space: pre-wrap; word-break: break-all;';
      container.appendChild(consoleBox);
    }
    
    consoleBox.textContent = `> Aplicando diff incremental a ${filepath}...\n\n`;
    
    try {
      const response = await fetch('/api/apply_diff', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filepath, diff: diffText })
      });
      
      if (response.ok) {
        const result = await response.json();
        consoleBox.textContent += result.message || "Parche aplicado.";
        buttonElement.textContent = "✅ Aplicado";
        buttonElement.style.color = "var(--accent-purple)";
      } else {
        const errorData = await response.json();
        consoleBox.textContent += `[ERROR]: ${errorData.error || 'Fallo de parche'}\n\n`;
        consoleBox.textContent += `Líneas del diff:\n${diffText}`;
        consoleBox.style.color = '#ff6b6b';
        buttonElement.textContent = "❌ Error";
      }
    } catch (err) {
      consoleBox.textContent += `[ERROR]: No se pudo conectar con el servidor local.`;
      consoleBox.style.color = '#ff6b6b';
      buttonElement.textContent = "❌ Error Red";
    } finally {
      buttonElement.disabled = false;
    }
  };

});
