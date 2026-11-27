<template>
  <AuthSetupView v-if="authGate === 'setup'" @completed="onAuthCompleted" />
  <LoginView v-else-if="authGate === 'login'" @authenticated="onAuthAuthenticated" />
  <div v-else class="min-h-screen flex flex-col font-sans selection:bg-blue-600 selection:text-white transition-colors duration-200"
    :class="isDarkTheme ? 'bg-[#18181b] text-zinc-100' : 'light-theme bg-zinc-100 text-zinc-900'">
    <!-- Top Header (Fiel ao ProxMenux Monitor) -->
    <header class="border-b px-4 lg:px-6 py-2.5 sticky top-0 z-50 transition-colors"
      :class="isDarkTheme ? 'bg-[#1f1f23] border-zinc-800' : 'bg-white border-zinc-200'">
      <div class="container mx-auto flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 sm:gap-4">
        <!-- Logo & Branding (Linux Menux official SVG logo) -->
        <div class="flex items-center gap-3 min-w-0">
          <img src="/logo.svg" alt="Linux Menux - Monitor" class="w-9 h-9 rounded-lg shadow-lg shadow-orange-500/20 shrink-0" />
          <div class="min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <h1 class="text-base font-bold text-white tracking-tight truncate">Linux Menux - Monitor</h1>
              <span class="text-xs bg-orange-500/10 text-orange-400 border border-orange-500/20 px-1.5 py-0.5 rounded tabular-nums font-semibold">v{{ appUpdateInfo?.current_version || APP_VERSION }}</span>
            </div>
            <p class="text-xs text-zinc-400 font-medium truncate">Painel do sistema {{ systemData.distro_name || 'Linux' }}</p>
          </div>
        </div>

        <!-- System Status Badges & Controls -->
        <div class="flex items-center gap-1.5 sm:gap-2 lg:gap-3 flex-wrap justify-between sm:justify-end">
          <!-- Node Selector Pill -->
          <div class="relative">
            <button @click="nodeDropdownOpen = !nodeDropdownOpen"
              class="bg-zinc-800/80 hover:bg-zinc-700/80 border border-zinc-700/60 text-xs text-zinc-200 px-3 py-1.5 rounded-lg flex items-center gap-1.5 tabular-nums shadow-sm cursor-pointer">
              <Server class="w-3.5 h-3.5 text-zinc-400" />
              <span>Nó: {{ systemData.hostname || 'linux-host' }}</span>
              <ChevronDown class="w-3 h-3 text-zinc-400 ml-0.5" />
            </button>
            <div v-if="nodeDropdownOpen" class="absolute right-0 top-full mt-1.5 w-64 bg-zinc-900 border border-zinc-700 rounded-xl shadow-2xl py-1.5 z-50 text-xs">
              <div class="px-3 py-1.5 text-zinc-400 font-semibold border-b border-zinc-800 flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
                <span>{{ systemData.hostname || 'linux-host' }} (Atual)</span>
              </div>
              <a v-for="n in linkedNodes.filter(x => !x.local)" :key="n.id" :href="n.url" target="_blank"
                class="block px-3 py-2 text-zinc-300 hover:bg-zinc-800 hover:text-white flex items-center justify-between">
                <span>{{ n.name }}</span>
                <span class="text-xs text-zinc-400">{{ n.tunnel ? 'Túnel' : n.product }}</span>
              </a>
              <button @click="nodeDropdownOpen = false; openLinkedNodesModal()"
                class="w-full text-left px-3 py-2 text-blue-400 hover:bg-zinc-800 font-semibold border-t border-zinc-800 mt-1 cursor-pointer">
                + Adicionar ou gerenciar nós...
              </button>
            </div>
          </div>

          <!-- Health Status -->
          <button @click="openHealthModal()"
            class="text-xs px-2.5 py-1 rounded-full font-medium flex items-center gap-1.5 transition cursor-pointer"
            :class="(systemData.available_updates || 0) > 0 ? 'bg-amber-500/10 text-amber-400 border border-amber-500/25 hover:bg-amber-500/20' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20'">
            <span class="w-1.5 h-1.5 rounded-full animate-pulse" :class="(systemData.available_updates || 0) > 0 ? 'bg-amber-400' : 'bg-emerald-500'"></span>
            {{ (systemData.available_updates || 0) > 0 ? 'Advertências' : 'Saudável' }}
          </button>

          <!-- Info Badge -->
          <button @click="openHealthModal('updates')"
            class="text-xs px-2.5 py-1 rounded-full font-medium flex items-center gap-1 transition cursor-pointer"
            :class="appUpdateInfo.update_available?.stable ? 'bg-amber-500/15 hover:bg-amber-500/25 text-amber-300 border border-amber-500/30 animate-pulse' : 'bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/20'">
            <Info class="w-3 h-3" />
            <span>{{ appUpdateInfo.update_available?.stable ? `Nova versão v${appUpdateInfo.latest_version}` : ((systemData.available_updates || 0) > 0 ? `${systemData.available_updates} atualizações` : '1 info') }}</span>
          </button>

          <!-- Uptime -->
          <div class="text-xs text-zinc-400 font-normal hidden sm:flex items-center gap-1">
            <Clock class="w-3.5 h-3.5 text-zinc-400" />
            <span>Tempo de atividade: {{ systemData.uptime || '1d 5h 20m' }}</span>
          </div>

          <!-- Refresh Button -->
          <button @click="refreshAllData" :disabled="loading" class="bg-zinc-800 hover:bg-zinc-700 active:scale-95 border border-zinc-700 text-zinc-300 text-xs px-3 py-1.5 rounded-lg font-medium flex items-center gap-1.5 transition cursor-pointer">
            <RefreshCw class="w-3.5 h-3.5 text-zinc-400" :class="{ 'animate-spin': loading }" />
            <span class="hidden md:inline">Atualizar</span>
          </button>

          <!-- Theme Toggle -->
          <button @click="toggleTheme" class="bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-zinc-300 p-1.5 rounded-lg transition cursor-pointer" title="Alternar Tema">
            <Moon v-if="isDarkTheme" class="w-3.5 h-3.5 text-zinc-400" />
            <Sun v-else class="w-3.5 h-3.5 text-amber-400" />
          </button>

          <!-- User Avatar -->
          <div class="relative">
            <button @click="userMenuOpen = !userMenuOpen"
              class="w-7 h-7 rounded-full bg-teal-600 hover:bg-teal-500 flex items-center justify-center text-xs font-bold text-white shadow ring-2 ring-zinc-700 cursor-pointer">
              {{ (currentUsername || 'A').slice(0, 1).toUpperCase() }}
            </button>
            <div v-if="userMenuOpen" class="absolute right-0 top-full mt-1.5 w-48 bg-zinc-900 border border-zinc-700 rounded-xl shadow-2xl py-1.5 z-50 text-xs">
              <div class="px-3 py-2 border-b border-zinc-800">
                <div class="font-bold text-white">{{ currentUsername || 'Administrador' }}</div>
                <div class="text-xs text-zinc-400">Sessão ativa</div>
              </div>
              <button @click="userMenuOpen = false; profileModalOpen = true" class="w-full text-left px-3 py-2 text-zinc-300 hover:bg-zinc-800 hover:text-white cursor-pointer">Ver perfil</button>
              <button @click="userMenuOpen = false; activeTab = 'admin-security'" class="w-full text-left px-3 py-2 text-zinc-300 hover:bg-zinc-800 hover:text-white cursor-pointer">Segurança</button>
              <button @click="logoutUser" class="w-full text-left px-3 py-2 text-red-400 hover:bg-zinc-800 border-t border-zinc-800 cursor-pointer">Sair</button>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Navigation Tabs Bar (Identical to ProxMenux: full-width grid-cols-7 pill container) -->
    <nav class="px-4 lg:px-6 pt-3 pb-1 relative z-40">
      <div class="container mx-auto">
        <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 w-full bg-[#242424] border border-zinc-800 rounded-xl p-1 gap-1">
        <!-- Tab: Visão Geral -->
        <button
          @click="activeTab = 'overview'"
          class="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition cursor-pointer"
          :class="activeTab === 'overview' ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30 font-semibold' : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/60'"
        >
          <LayoutDashboard class="w-4 h-4 shrink-0" />
          <span class="truncate">Visão geral</span>
        </button>

        <!-- Tab: Apps -->
        <button
          @click="activeTab = 'apps'"
          class="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition cursor-pointer"
          :class="activeTab === 'apps' ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30 font-semibold' : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/60'"
        >
          <Grid3x3 class="w-4 h-4 shrink-0" />
          <span class="truncate">Apps</span>
        </button>

        <!-- Tab: Containers & Stacks -->
        <button
          @click="activeTab = 'containers'"
          class="w-full flex items-center justify-center gap-1.5 px-2 py-2 rounded-lg text-xs font-medium transition cursor-pointer"
          :class="activeTab === 'containers' ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30 font-semibold' : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/60'"
        >
          <Boxes class="w-4 h-4 shrink-0" />
          <span class="whitespace-nowrap">Containers</span>
        </button>

        <!-- Tab: Nó (Dropdown: Armazenar, Rede, Fluxo de Redes, Hardware) -->
        <div class="relative group w-full">
          <button
            @click="nodeMenuOpen = !nodeMenuOpen; adminMenuOpen = false"
            class="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition cursor-pointer"
            :class="(activeTab === 'storage' || activeTab.startsWith('network') || activeTab === 'hardware') ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30 font-semibold' : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/60'"
          >
            <Server class="w-4 h-4 shrink-0" />
            <span class="truncate">{{ activeTab === 'storage' ? 'Armazenar' : (activeTab.startsWith('network') ? 'Rede' : (activeTab === 'hardware' ? 'Hardware' : 'Nó')) }}</span>
            <ChevronDown class="w-3.5 h-3.5 ml-0.5 opacity-70 shrink-0" />
          </button>
          <div class="absolute left-0 top-full w-52 bg-zinc-900 border border-zinc-800 rounded-lg shadow-xl py-1.5 z-50 group-hover:block"
            :class="nodeMenuOpen ? 'block' : 'hidden'">
            <button @click="activeTab = 'storage'; nodeMenuOpen = false" class="w-full text-left px-3.5 py-2 text-xs font-medium text-zinc-300 hover:bg-zinc-800 hover:text-white flex items-center gap-2 cursor-pointer">
              <HardDrive class="w-3.5 h-3.5 text-blue-400" />
              <span>Armazenar</span>
            </button>
            <button @click="activeTab = 'network-overview'; nodeMenuOpen = false" class="w-full text-left px-3.5 py-2 text-xs font-medium text-zinc-300 hover:bg-zinc-800 hover:text-white flex items-center gap-2 cursor-pointer">
              <Network class="w-3.5 h-3.5 text-emerald-400" />
              <span>Rede</span>
            </button>
            <button @click="activeTab = 'network-flow'; nodeMenuOpen = false" class="w-full text-left px-3.5 py-2 text-xs font-medium text-zinc-300 hover:bg-zinc-800 hover:text-white flex items-center gap-2 cursor-pointer">
              <Share2 class="w-3.5 h-3.5 text-blue-400" />
              <span>Fluxo de Redes</span>
            </button>
            <button @click="activeTab = 'hardware'; nodeMenuOpen = false" class="w-full text-left px-3.5 py-2 text-xs font-medium text-zinc-300 hover:bg-zinc-800 hover:text-white flex items-center gap-2 cursor-pointer">
              <Cpu class="w-3.5 h-3.5 text-amber-400" />
              <span>Hardware</span>
            </button>
          </div>
        </div>

        <!-- Tab: Armazenamento -->
        <button
          @click="activeTab = 'backup'"
          class="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition cursor-pointer"
          :class="activeTab === 'backup' ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30 font-semibold' : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/60'"
        >
          <DatabaseBackup class="w-4 h-4 shrink-0" />
          <span class="truncate">Backup</span>
        </button>

        <!-- Tab: Terminal -->
        <button
          @click="activeTab = 'terminal'"
          class="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition cursor-pointer"
          :class="activeTab === 'terminal' ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30 font-semibold' : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/60'"
        >
          <Terminal class="w-4 h-4 shrink-0" />
          <span class="truncate">Terminal</span>
        </button>

        <!-- Tab: Administrador -->
        <div class="relative group w-full">
          <button
            @click="adminMenuOpen = !adminMenuOpen; nodeMenuOpen = false"
            class="w-full flex items-center justify-center gap-1.5 px-2 py-2 rounded-lg text-xs font-medium transition cursor-pointer"
            :class="activeTab.startsWith('admin') ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30 font-semibold' : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/60'"
          >
            <Settings2 class="w-4 h-4 shrink-0" />
            <span class="truncate">{{
              activeTab === 'admin-logs' ? 'Registros' :
              activeTab === 'admin-security' ? 'Segurança' :
              activeTab === 'admin-audit' ? 'Auditoria' :
              activeTab === 'admin-settings' ? 'Configurações' :
              activeTab === 'admin-about' ? 'Sobre' : 'Administrador'
            }}</span>
            <ChevronDown class="w-3.5 h-3.5 ml-0.5 opacity-70 shrink-0" />
          </button>
          <div class="absolute right-0 top-full w-56 bg-zinc-900 border border-zinc-800 rounded-lg shadow-xl py-1.5 z-50 group-hover:block"
            :class="adminMenuOpen ? 'block' : 'hidden'">
            <button @click="activeTab = 'admin-logs'; adminMenuOpen = false" class="w-full text-left px-3.5 py-2 text-xs font-medium text-zinc-300 hover:bg-zinc-800 hover:text-white cursor-pointer">Registros do sistema</button>
            <button @click="activeTab = 'admin-security'; adminMenuOpen = false" class="w-full text-left px-3.5 py-2 text-xs font-medium text-zinc-300 hover:bg-zinc-800 hover:text-white cursor-pointer">Segurança</button>
            <button @click="activeTab = 'admin-audit'; adminMenuOpen = false" class="w-full text-left px-3.5 py-2 text-xs font-medium text-zinc-300 hover:bg-zinc-800 hover:text-white cursor-pointer">Auditoria e relatórios</button>
            <button @click="activeTab = 'admin-settings'; adminMenuOpen = false" class="w-full text-left px-3.5 py-2 text-xs font-medium text-zinc-300 hover:bg-zinc-800 hover:text-white cursor-pointer">Configurações</button>
            <button @click="activeTab = 'admin-about'; adminMenuOpen = false" class="w-full text-left px-3.5 py-2 text-xs font-medium text-zinc-300 hover:bg-zinc-800 hover:text-white border-t border-zinc-800 mt-1 pt-2 cursor-pointer">Sobre</button>
          </div>
        </div>
        </div>
      </div>
    </nav>

    <!-- Main Content Area -->
    <main class="flex-1 container w-full mx-auto px-4 md:px-6 py-4 md:py-6 space-y-6">

      <!-- ========================================================================================= -->
      <!-- TAB 1: VISÃO GERAL (OVERVIEW - MODULAR 1:1)                                           -->
      <!-- ========================================================================================= -->
      <OverviewView
        v-if="activeTab === 'overview'"
        ref="overviewRef"
        :system-data="systemData"
        :container-stats="containerStats"
        :network-data="networkData"
        :physical-disks="physicalDisks"
        :unique-mounts="uniqueMounts"
        :total-storage-formatted="totalStorageFormatted"
        :total-used-storage-formatted="totalUsedStorageFormatted"
        :total-storage-t-b="totalStorageTB"
        :free-storage-formatted="freeStorageFormatted"
        :total-storage-percent="totalStoragePercent"
        v-model:timeframe="timeframe"
        v-model:net-timeframe="netTimeframe"
        :cpu-stats="cpuStats"
        :mem-stats="memStats"
        :net-period-stats="netPeriodStats"
        :net-period-label="netPeriodLabel"
        :metrics-loading="metricsLoading"
        :net-metrics-loading="netMetricsLoading"
        @open-cpu="openCpuModal()"
        @open-mem="openMemModal()"
        @open-temp="openTempModal()"
        @go-containers="activeTab = 'containers'"
        @open-health="(cat) => openHealthModal(cat)"
      />

      <!-- ========================================================================================= -->
      <!-- TAB 2: APPS DASHBOARD (MODULAR 1:1 - EDITÁVEL)                                           -->
      <!-- ========================================================================================= -->
      <AppsView
        v-if="activeTab === 'apps'"
        :apps="allApps"
        :overrides="appOverrides"
        @open-add="customLinkModal = true"
        @delete-custom="removeCustomLink"
        @save-override="saveAppOverride"
      />

      <!-- ========================================================================================= -->
      <!-- TAB 3: CONTAINERS & STACKS (DOCKER / SWARM / DOKPLOY)                                     -->
      <!-- ========================================================================================= -->
      <ContainersView
        v-if="activeTab === 'containers'"
        :containers="containers"
        :container-stats="containerStats"
        :system-data="systemData"
        :disk-used-gb="totalUsedStorageFormatted.replace(' GB', '')"
        :disk-total-gb="totalStorageFormatted.replace(' GB', '')"
        :disk-percent="totalStoragePercent"
        :updates-map="containerUpdatesMap"
        :updates-count="containersWithUpdatesCount"
        :checking-updates="checkingContainerUpdates"
        :updating-id="updatingContainerId"
        @check-updates="fetchContainerUpdates(true)"
        @update-container="updateSingleContainer"
        @restart-container="restartContainer"
        @open-logs="openContainerLogs"
        @refresh="fetchTelemetry"
      />

      <!-- ========================================================================================= -->
      <!-- TAB 4: REDE (MODULAR 1:1)                                                                -->
      <!-- ========================================================================================= -->
      <NetworkView
        v-if="activeTab.startsWith('network')"
        ref="networkRef"
        v-model:active-tab="activeTab"
        :network-data="networkData"
        :system-data="systemData"
        :flow-data="flowData"
        :flow-consumers="flowConsumers"
        :ai-loading="aiLoading"
        :ai-report="aiReport"
        @run-ai="runAiDiagnosis"
        @open-iface="openIfaceModal"
      />

      <!-- ========================================================================================= -->
      <!-- TAB 5: ARMAZENAMENTO (MODULAR 1:1 PROXMENUX)                                           -->
      <!-- ========================================================================================= -->
      <StorageView
        v-if="activeTab === 'storage'"
        :disks="physicalDisks"
        :mounts="systemData.mounts || []"
        :total-formatted="totalStorageFormatted"
        :free-formatted="freeStorageFormatted"
        :total-percent="totalStoragePercent"
        @refresh-disks="fetchStorageDisks"
        @open-disk="openDiskModal"
      />

      <!-- ========================================================================================= -->
      <!-- TAB 6: BACKUP                                                                             -->
      <!-- ========================================================================================= -->
      <HardwareView
        v-if="activeTab === 'hardware'"
        :hardware-data="hardwareData"
        :loading="hardwareLoading"
      />

      <!-- ========================================================================================= -->
      <!-- TAB 6: BACKUP (REAL MULTI-DISTRO - VÍDEO 1)                                               -->
      <!-- ========================================================================================= -->
      <!-- TAB 6: BACKUP (MODULAR 1:1 COM DESTINO LOCAL / BORG / CLOUDFLARE R2)             -->
      <!-- ========================================================================================= -->
      <BackupView
        v-if="activeTab === 'backup'"
        :backup-data="backupData"
        :backup-running="backupRunning"
        v-model:new-path="newBackupPath"
        @run-backup="triggerManualBackup"
        @add-path="addCustomBackupPath"
        @remove-path="removeCustomBackupPath"
        @delete-backup="deleteBackup"
        @refresh="fetchBackups"
      />

      <!-- ========================================================================================= -->
      <!-- TAB 7: TERMINAL INTERATIVO PTY                                                            -->
      <!-- ========================================================================================= -->
      <TerminalView
        v-if="activeTab === 'terminal'"
        ref="terminalRef"
        :connected="terminalConnected"
        :connecting="terminalConnecting"
        @reconnect="reconnectTerminal"
        @send="sendTerminalCommand"
      />

      <!-- ========================================================================================= -->
      <!-- TAB 8: ADMINISTRADOR & NOTIFICAÇÕES 100% PT-BR                                             -->
      <!-- ========================================================================================= -->
      <section v-if="activeTab.startsWith('admin')" class="space-y-6 animate-fadeIn">

        <!-- 8.1 REGISTROS DO SISTEMA -->
        <LogsView
          v-if="activeTab === 'admin-logs'"
          :logs-data="logsData"
          :backup-data="backupData"
          v-model:search="logsSearch"
          v-model:level="logsLevel"
          v-model:since="logsSince"
          v-model:unit="logsUnit"
          @refresh="fetchLogs"
          @export="exportLogs"
        />

        <!-- 8.2 SEGURANÇA -->
        <!-- 8.2 SEGURANÇA (MODULAR) -->
        <SecurityView
          v-if="activeTab === 'admin-security'"
          :security-data="securityData"
          v-model:new-fw-port="newFwPort"
          v-model:new-fw-proto="newFwProto"
          v-model:new-fw-action="newFwAction"
          v-model:new-token-name="newTokenName"
          :last-generated-token="lastGeneratedToken"
          :sec-installing="secInstalling"
          :lynis-running="lynisRunning"
          @add-fw-rule="addFwRule"
          @refresh-security="fetchSecurity"
          @generate-token="generateApiToken"
          @revoke-token="revokeApiToken"
          @install-tool="installSecTool"
          @run-lynis="triggerLynisAudit"
        />

        <!-- 8.3 AUDITORIA (MODULAR) -->
        <AuditView
          v-if="activeTab === 'admin-audit'"
          :audit-data="auditData"
          @refresh="fetchAuditReport"
        />

        <!-- 8.4 CONFIGURAÇÕES (MODULAR 1:1 PROXMENUX - SALVA NO BACKEND) -->
        <SettingsView
          v-if="activeTab === 'admin-settings' || activeTab === 'admin'"
          :settings-data="settingsData"
          :interfaces="networkData.interfaces || []"
          :physical-disks="physicalDisks"
          v-model:telegram-token="telegramToken"
          v-model:telegram-chat-id="telegramChatId"
          v-model:discord-webhook="discordWebhook"
          v-model:ai-api-key="aiApiKey"
          v-model:ai-model="aiModel"
          @save="saveAdminSettings"
          @reset-thresholds="resetThresholds"
          @test-telegram="testTelegram"
          @test-discord="testDiscord"
        />

        <!-- 8.5 SOBRE (MODULAR) -->
        <AboutView v-if="activeTab === 'admin-about'" />
      </section>

      <!-- Modais Modulares (100% desacoplados em components/) -->
      <CustomLinkModal
        :open="customLinkModal"
        v-model:name="newLinkName"
        v-model:url="newLinkUrl"
        v-model:category="newLinkCategory"
        v-model:logo="newLinkLogo"
        @close="customLinkModal = false"
        @save="saveCustomLink"
      />
      <HealthStatusModal
        :open="healthModalOpen"
        :loading="healthLoading"
        :health-data="healthData"
        :distro-id="systemData.distro_id"
        :distro-name="systemData.distro_name"
        :app-update-info="appUpdateInfo"
        :app-updating="appUpdating"
        :app-update-msg="appUpdateMsg"
        v-model:expanded-cat="expandedHealthCat"
        @close="healthModalOpen = false"
        @open-update="openSystemUpdateModal()"
        @refresh-updates="openHealthModal('updates', true)"
        @self-update="triggerAppSelfUpdate()"
      />
      <SystemUpdateModal
        ref="updateModalRef"
        :open="updateModalOpen"
        :ws-state="updateWsState"
        :distro-id="systemData.distro_id"
        :distro-name="systemData.distro_name"
        @close="closeSystemUpdateModal()"
      />
      <AppSelfUpdateModal
        :open="selfUpdateModalOpen"
        :target-version="selfUpdateTarget"
        :log-content="selfUpdateLog"
        :status="selfUpdateStatus"
        :status-message="selfUpdateStatusMsg"
        @close="closeSelfUpdateModal()"
        @reload="reloadAfterSelfUpdate()"
      />
      <DiskDetailModal
        :open="diskModalOpen"
        :disk="selectedDisk"
        :active-tab="diskModalTab"
        :smart-detail="smartDetail"
        :smart-history="smartHistory"
        :smart-schedules="smartSchedules"
        :smart-installing="smartInstalling"
        v-model:cron-value="newSmartCron"
        @close="diskModalOpen = false"
        @change-tab="(t) => diskModalTab = t"
        @install-smart="installSmartTools"
        @run-smart="triggerSmartTest"
        @add-schedule="addSmartSchedule"
      />
      <LinkedNodesModal
        :open="linkedNodesModalOpen"
        :nodes="linkedNodes"
        v-model:name="newNodeName"
        v-model:url="newNodeUrl"
        v-model:tunnel="newNodeTunnel"
        @close="linkedNodesModalOpen = false"
        @save="saveLinkedNode"
        @remove="removeLinkedNode"
      />
      <ProfileModal
        :open="profileModalOpen"
        @close="profileModalOpen = false"
        @open-security="profileModalOpen = false; activeTab = 'admin-security'"
      />
      <ContainerLogsModal
        :open="containerLogsModalOpen"
        :title="containerLogsTitle"
        :logs="containerLogsText"
        @close="containerLogsModalOpen = false"
      />
      <ProcessDetailModal
        :open="cpuModalOpen || memModalOpen"
        :mode="cpuModalOpen ? 'cpu' : 'mem'"
        @close="closeProcessModal()"
      />
      <TemperatureDetailModal
        :open="tempModalOpen"
        :live-temperature="Number(systemData.temperature || 0)"
        @close="tempModalOpen = false"
      />
      <NetworkInterfaceModal
        :open="ifaceModalOpen"
        :detail="ifaceDetail"
        @close="ifaceModalOpen = false"
      />
      <OnboardingCarousel
        :open="onboardingOpen"
        @close="onboardingOpen = false; checkFirstVisitModals()"
      />
      <ReleaseNotesModal
        :open="releaseNotesOpen"
        @close="releaseNotesOpen = false"
      />
    </main>

    <!-- Footer -->
    <footer class="bg-[#18181b] border-t border-zinc-800/80 px-6 py-4 text-center text-xs text-zinc-400 tabular-nums">
      Linux Menux - Monitor v{{ appUpdateInfo?.current_version || APP_VERSION }} · Painel de Controle Linux, Docker Swarm & Dokploy · Multi-Distro
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick, watch } from 'vue'
import {
  LayoutDashboard, Grid3x3, Boxes, Network, HardDrive, DatabaseBackup,
  Terminal, Settings2, Server, ChevronDown, ChevronRight, Info, Clock,
  RefreshCw, Moon, Sun, Activity, Wifi, Cpu, Thermometer, Plus, ExternalLink,
  Share2, Sparkles, CheckCircle, ShieldCheck, Send, MessageSquare, Search, Trash2
} from 'lucide-vue-next'
import {
  Chart, LineController, LineElement, PointElement, LinearScale,
  CategoryScale, Title, Tooltip, Legend, Filler
} from 'chart.js'
import { Terminal as XTerm } from 'xterm'
import { FitAddon } from 'xterm-addon-fit'
import 'xterm/css/xterm.css'
import ProcessDetailModal from './components/ProcessDetailModal.vue'
import TemperatureDetailModal from './components/TemperatureDetailModal.vue'
import ContainersView from './components/ContainersView.vue'
import SettingsView from './components/SettingsView.vue'
import AppsView from './components/AppsView.vue'
import StorageView from './components/StorageView.vue'
import DiskDetailModal from './components/DiskDetailModal.vue'
import BackupView from './components/BackupView.vue'
import LogsView from './components/LogsView.vue'
import OverviewView from './components/OverviewView.vue'
import NetworkView from './components/NetworkView.vue'
import HardwareView from './components/HardwareView.vue'
import TerminalView from './components/TerminalView.vue'
import SecurityView from './components/SecurityView.vue'
import AuditView from './components/AuditView.vue'
import AboutView from './components/AboutView.vue'
import CustomLinkModal from './components/CustomLinkModal.vue'
import HealthStatusModal from './components/HealthStatusModal.vue'
import SystemUpdateModal from './components/SystemUpdateModal.vue'
import AppSelfUpdateModal from './components/AppSelfUpdateModal.vue'
import LinkedNodesModal from './components/LinkedNodesModal.vue'
import ProfileModal from './components/ProfileModal.vue'
import ContainerLogsModal from './components/ContainerLogsModal.vue'
import NetworkInterfaceModal from './components/NetworkInterfaceModal.vue'
import DistroLogo from './components/DistroLogo.vue'
import AuthSetupView from './components/AuthSetupView.vue'
import LoginView from './components/LoginView.vue'
import OnboardingCarousel from './components/OnboardingCarousel.vue'
import ReleaseNotesModal from './components/ReleaseNotesModal.vue'
import { getAuthToken, setAuthToken } from './lib/api-config'
import { APP_VERSION } from './lib/version'

const authGate = ref('ready')
const currentUsername = ref('AlaxRicard')
const onboardingOpen = ref(false)
const releaseNotesOpen = ref(false)

function toggleTheme() {
  isDarkTheme.value = !isDarkTheme.value
  try {
    localStorage.setItem('linuxmenux-theme', isDarkTheme.value ? 'dark' : 'light')
  } catch {}
}

function logoutUser() {
  userMenuOpen.value = false
  setAuthToken('')
  authGate.value = 'login'
}

function checkFirstVisitModals() {
  try {
    if (!localStorage.getItem('linuxmenux-onboarding-done')) {
      onboardingOpen.value = true
    } else if (localStorage.getItem('linuxmenux-last-seen-version') !== APP_VERSION) {
      releaseNotesOpen.value = true
    }
  } catch {}
}

async function onAuthCompleted(payload) {
  currentUsername.value = payload?.username || 'admin'
  authGate.value = 'ready'
  checkFirstVisitModals()
  await startDashboardSession()
}

async function onAuthAuthenticated(payload) {
  currentUsername.value = payload?.username || 'admin'
  authGate.value = 'ready'
  checkFirstVisitModals()
  await startDashboardSession()
}

Chart.register(LineController, LineElement, PointElement, LinearScale, CategoryScale, Title, Tooltip, Legend, Filler)

// Navigation State (persiste aba atual no F5 via URL hash + localStorage)
const VALID_TABS = new Set([
  'overview',
  'apps',
  'containers',
  'storage',
  'network',
  'network-overview',
  'network-flow',
  'network-interfaces',
  'hardware',
  'backup',
  'terminal',
  'admin',
  'admin-logs',
  'admin-security',
  'admin-audit',
  'admin-settings',
  'admin-about',
])

function resolveInitialTab() {
  if (typeof window !== 'undefined') {
    const hashTab = window.location.hash.replace(/^#/, '').trim()
    if (VALID_TABS.has(hashTab)) return hashTab
    const saved = localStorage.getItem('linuxmenux-active-tab') || ''
    if (VALID_TABS.has(saved)) return saved
  }
  return 'overview'
}

const activeTab = ref(resolveInitialTab())

watch(activeTab, (tab) => {
  if (typeof window === 'undefined' || !VALID_TABS.has(tab)) return
  try {
    localStorage.setItem('linuxmenux-active-tab', tab)
    if (window.location.hash !== `#${tab}`) {
      window.history.replaceState(null, '', `#${tab}`)
    }
  } catch {}
}, { immediate: true })

if (typeof window !== 'undefined') {
  window.addEventListener('hashchange', () => {
    const hashTab = window.location.hash.replace(/^#/, '').trim()
    if (VALID_TABS.has(hashTab) && activeTab.value !== hashTab) {
      activeTab.value = hashTab
    }
  })
}
const nodeMenuOpen = ref(false)
const adminMenuOpen = ref(false)
const loading = ref(false)
const metricsLoading = ref(false)
const netMetricsLoading = ref(false)
const readSavedPref = (key, fallback) => {
  try {
    const v = localStorage.getItem(key)
    return v !== null && v !== '' ? v : fallback
  } catch { return fallback }
}
const timeframe = ref(readSavedPref('linuxmenux-overview-timeframe', 'day'))
const netTimeframe = ref(readSavedPref('linuxmenux-overview-net-timeframe', 'day'))
watch(timeframe, (v) => { try { localStorage.setItem('linuxmenux-overview-timeframe', v) } catch {} })
watch(netTimeframe, (v) => { try { localStorage.setItem('linuxmenux-overview-net-timeframe', v) } catch {} })

const cpuStats = ref({ avg: 0, max: 0, min: 0 })
const memStats = ref({ avg: 0, max: 0, min: 0 })
const netPeriodStats = ref({ rx_gb: 0, tx_gb: 0 })
const netPeriodLabel = computed(() => {
  const map = { hour: '1h', day: '24h', week: '7d', month: '30d', year: '1y' }
  return map[netTimeframe.value] || '24h'
})

const uniqueMounts = computed(() => {
  const seen = new Set()
  const out = []
  for (const m of (systemData.value?.mounts || [])) {
    const key = m.device || m.mountpoint
    if (!seen.has(key)) {
      seen.add(key)
      out.push(m)
    }
  }
  return out
})

const totalStorageFormatted = computed(() => {
  const total = uniqueMounts.value.reduce((acc, m) => acc + (m.total_bytes || 0), 0)
  return total > 0 ? (total / (1024 ** 3)).toFixed(1) + ' GB' : '0 GB'
})

const totalUsedStorageFormatted = computed(() => {
  const used = uniqueMounts.value.reduce((acc, m) => acc + (m.used_bytes || 0), 0)
  return used > 0 ? (used / (1024 ** 3)).toFixed(1) + ' GB' : '0 GB'
})

const totalStorageTB = computed(() => {
  const total = uniqueMounts.value.reduce((acc, m) => acc + (m.total_bytes || 0), 0)
  return total > 0 ? (total / (1024 ** 4)).toFixed(1) + ' TB' : '0.0 TB'
})

const freeStorageFormatted = computed(() => {
  const avail = uniqueMounts.value.reduce((acc, m) => acc + (m.available_bytes || 0), 0)
  return avail > 0 ? (avail / (1024 ** 3)).toFixed(1) + ' GB' : '0 GB'
})

const totalStoragePercent = computed(() => {
  const total = uniqueMounts.value.reduce((acc, m) => acc + (m.total_bytes || 0), 0)
  const used = uniqueMounts.value.reduce((acc, m) => acc + (m.used_bytes || 0), 0)
  return total > 0 ? Math.round((used / total) * 100) : 0
})

// Modals
const cpuModalOpen = ref(false)
const memModalOpen = ref(false)
const tempModalOpen = ref(false)
function openCpuModal() { cpuModalOpen.value = true; memModalOpen.value = false }
function openMemModal() { memModalOpen.value = true; cpuModalOpen.value = false }
function closeProcessModal() { cpuModalOpen.value = false; memModalOpen.value = false }
function openTempModal() { tempModalOpen.value = true }
function handleGlobalEscape(e) {
  if (e.key !== 'Escape') return
  customLinkModal.value = false
  healthModalOpen.value = false
  updateModalOpen.value = false
  diskModalOpen.value = false
  linkedNodesModalOpen.value = false
  profileModalOpen.value = false
  containerLogsModalOpen.value = false
  ifaceModalOpen.value = false
}
const customLinkModal = ref(false)
const healthModalOpen = ref(false)
const healthLoading = ref(false)
const healthData = ref({})
const expandedHealthCat = ref('updates')
const updateModalOpen = ref(false)
// updateTerminalContainer provided via updateModalRef computed above
const updateWsState = ref('offline')
let updateXterm = null
let updateFitAddon = null
let updateWs = null

const isDarkTheme = ref(true)
const nodeDropdownOpen = ref(false)
const userMenuOpen = ref(false)
const profileModalOpen = ref(false)
const linkedNodesModalOpen = ref(false)
const linkedNodes = ref([])
const newNodeName = ref('')
const newNodeUrl = ref('')
const newNodeTunnel = ref(false)

async function openLinkedNodesModal() {
  linkedNodesModalOpen.value = true
  const res = await fetch('/api/monitor-links')
  if (res.ok) { const j = await res.json(); linkedNodes.value = j.links || [] }
}
async function saveLinkedNode() {
  if (!newNodeName.value.trim() || !newNodeUrl.value.trim()) return
  await fetch('/api/monitor-links', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: newNodeName.value, url: newNodeUrl.value, tunnel: newNodeTunnel.value })
  })
  newNodeName.value = ''; newNodeUrl.value = ''; newNodeTunnel.value = false
  await openLinkedNodesModal()
}
async function removeLinkedNode(id) {
  await fetch(`/api/monitor-links/${id}`, { method: 'DELETE' })
  await openLinkedNodesModal()
}

// Storage & SMART
const physicalDisks = ref([])
const smartHistory = ref([])
const smartSchedules = ref({ enabled: true, items: [] })
const diskModalOpen = ref(false)
const diskModalTab = ref('overview')
const selectedDisk = ref(null)
const smartDetail = ref({ installed: false, attributes: [] })
const smartInstalling = ref(false)
const newSmartCron = ref('0 3 * * 0')

async function fetchStorageDisks() {
  const res = await fetch('/api/storage/disks')
  if (res.ok) {
    const j = await res.json()
    physicalDisks.value = j.disks || []
    smartHistory.value = j.history || []
    smartSchedules.value = j.schedules || { enabled: true, items: [] }
  }
}
async function openDiskModal(d) {
  selectedDisk.value = d; diskModalTab.value = 'overview'; diskModalOpen.value = true
  const res = await fetch(`/api/storage/smart?device=${encodeURIComponent(d.device)}`)
  if (res.ok) smartDetail.value = await res.json()
}
async function installSmartTools() {
  smartInstalling.value = true
  try {
    const res = await fetch('/api/storage/smart/install', { method: 'POST' })
    const j = await res.json()
    if (!j.success) alert(j.message || 'Erro ao instalar')
    if (selectedDisk.value) await openDiskModal(selectedDisk.value)
    await fetchStorageDisks()
  } finally { smartInstalling.value = false }
}
async function triggerSmartTest(mode) {
  if (!selectedDisk.value) return
  const res = await fetch('/api/storage/smart/test', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ device: selectedDisk.value.device, mode })
  })
  const j = await res.json()
  alert(j.message || 'Teste iniciado')
  await fetchStorageDisks()
}
async function addSmartSchedule() {
  if (!selectedDisk.value) return
  const res = await fetch('/api/storage/smart/schedule', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ device: selectedDisk.value.device, mode: 'short', cron: newSmartCron.value })
  })
  if (res.ok) smartSchedules.value = await res.json()
}

// Hardware Full
const hardwareLoading = ref(false)
const hardwareData = ref({})
async function fetchHardwareFull() {
  hardwareLoading.value = true
  try {
    const res = await fetch('/api/hardware/full')
    if (res.ok) hardwareData.value = await res.json()
  } finally { hardwareLoading.value = false }
}

// Backup
const backupData = ref({ destination: '/var/backups/linuxmenux', custom_paths: [], backups: [] })
const newBackupPath = ref('')
const backupRunning = ref(false)
async function fetchBackups() {
  const res = await fetch('/api/backups')
  if (res.ok) backupData.value = await res.json()
}
async function addCustomBackupPath() {
  if (!newBackupPath.value.trim()) return
  await fetch('/api/backup/paths', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ path: newBackupPath.value }) })
  newBackupPath.value = ''
  await fetchBackups()
}
async function removeCustomBackupPath(p) {
  await fetch(`/api/backup/paths?path=${encodeURIComponent(p)}`, { method: 'DELETE' })
  await fetchBackups()
}
async function triggerManualBackup() {
  backupRunning.value = true
  try {
    const res = await fetch('/api/backup/run', { method: 'POST' })
    const j = await res.json()
    if (!j.success) alert(j.message || 'Erro no backup')
    await fetchBackups()
  } finally { backupRunning.value = false }
}
async function deleteBackup(name) {
  await fetch(`/api/backup/${encodeURIComponent(name)}`, { method: 'DELETE' })
  await fetchBackups()
}

// Admin: Logs, Security, Audit, Settings
const logsData = ref({ entries: [], total: 0, errors: 0, warnings: 0 })
const logsSearch = ref('')
const logsLevel = ref(readSavedPref('linuxmenux-logs-level', 'all'))
const logsSince = ref(readSavedPref('linuxmenux-logs-since', '24h'))
const logsUnit = ref(readSavedPref('linuxmenux-logs-unit', 'all'))
watch(logsLevel, (v) => { try { localStorage.setItem('linuxmenux-logs-level', v) } catch {} })
watch(logsSince, (v) => { try { localStorage.setItem('linuxmenux-logs-since', v) } catch {} })
watch(logsUnit, (v) => { try { localStorage.setItem('linuxmenux-logs-unit', v) } catch {} })
async function fetchLogs() {
  const res = await fetch(`/api/events?search=${encodeURIComponent(logsSearch.value)}&level=${logsLevel.value}&since=${logsSince.value}&unit=${encodeURIComponent(logsUnit.value)}`)
  if (res.ok) logsData.value = await res.json()
}
function exportLogs() {
  const lines = (logsData.value.entries || []).map(e => `[${e.timestamp}] [${e.level}] ${e.unit} (PID ${e.pid}): ${e.message}`).join('\n')
  const blob = new Blob([lines || 'Sem registros.'], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `linuxmenux-logs-${new Date().toISOString().slice(0, 10)}.log`
  a.click()
  URL.revokeObjectURL(url)
}
const newFwPort = ref('')
const newFwProto = ref('tcp')
const newFwAction = ref('allow')
async function addFwRule() {
  if (!newFwPort.value.trim()) return
  const res = await fetch('/api/security/firewall/rule', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ port: newFwPort.value.trim(), proto: newFwProto.value, action: newFwAction.value })
  })
  const j = await res.json()
  if (!j.success) alert(j.message || 'Erro ao adicionar regra')
  newFwPort.value = ''
  await fetchSecurity()
}
const securityData = ref({ firewall: {}, tailscale: {}, fail2ban: {}, lynis: {}, api_tokens: [] })
const newTokenName = ref('')
const lastGeneratedToken = ref('')
const secInstalling = ref('')
const lynisRunning = ref(false)
async function fetchSecurity() {
  const res = await fetch('/api/security/overview')
  if (res.ok) securityData.value = await res.json()
}
async function generateApiToken() {
  const res = await fetch('/api/auth/api-tokens', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: newTokenName.value || 'API Token' }) })
  if (res.ok) { const j = await res.json(); lastGeneratedToken.value = j.token; newTokenName.value = ''; await fetchSecurity() }
}
async function revokeApiToken(id) {
  await fetch(`/api/auth/api-tokens/${id}`, { method: 'DELETE' })
  await fetchSecurity()
}
async function installSecTool(tool) {
  secInstalling.value = tool
  try {
    const res = await fetch(`/api/security/install/${tool}`, { method: 'POST' })
    const j = await res.json()
    if (!j.success) alert(j.message || 'Erro ao instalar')
    await fetchSecurity()
  } finally { secInstalling.value = '' }
}
async function triggerLynisAudit() {
  lynisRunning.value = true
  try {
    const res = await fetch('/api/security/lynis/run', { method: 'POST' })
    const j = await res.json().catch(() => ({}))
    if (!res.ok || j.success === false) {
      alert(j.message || j.detail || 'Erro ao iniciar auditoria Lynis.')
      return
    }
    for (let i = 0; i < 120; i++) {
      await new Promise((r) => setTimeout(r, 2000))
      const stRes = await fetch('/api/security/lynis/status').catch(() => null)
      if (!stRes || !stRes.ok) continue
      const st = await stRes.json().catch(() => ({}))
      if (!st.running) {
        if (st.success === false) {
          alert(st.message || 'Erro ao executar auditoria Lynis.')
        }
        break
      }
    }
    await fetchSecurity()
  } finally { lynisRunning.value = false }
}
const auditData = ref({ items: [], counts: {} })
async function fetchAuditReport() {
  const res = await fetch('/api/audit/report')
  if (res.ok) auditData.value = await res.json()
}
const aiApiKey = ref('')
const aiModel = ref('nvidia/nemotron-3-nano-30b-a3b:reasoning:free')
const settingsData = ref({
  language: 'pt-BR',
  network_unit: 'bytes',
  excluded_interfaces: [],
  excluded_disks: [],
  thresholds: { cpu_warn: 80, cpu_crit: 90, mem_warn: 85, mem_crit: 95, temp_warn: 75, disk_warn: 90 }
})
function resetThresholds() {
  settingsData.value.thresholds = { cpu_warn: 80, cpu_crit: 90, mem_warn: 85, mem_crit: 95, temp_warn: 75, disk_warn: 90 }
}
async function fetchAdminSettings() {
  const res = await fetch('/api/settings')
  if (res.ok) {
    const j = await res.json()
    const ai = j.ai || {}
    const notif = j.notifications || {}
    settingsData.value = {
      ...settingsData.value,
      ...j,
      language: j.language || 'pt-BR',
      network_unit: j.network_unit || 'bytes',
      ai_provider: ai.provider || j.ai_provider || 'openrouter',
      ai_enabled: Boolean(ai.enabled ?? j.ai_enabled ?? false),
      notifications_enabled: notif.enabled !== false && j.notifications_enabled !== false,
      thresholds: { cpu_warn: 80, cpu_crit: 90, mem_warn: 85, mem_crit: 95, temp_warn: 75, disk_warn: 90, ...(j.thresholds || {}) },
    }
    telegramToken.value = notif.telegram_token || ''
    telegramChatId.value = notif.telegram_chat_id || ''
    discordWebhook.value = notif.discord_webhook || ''
    aiApiKey.value = ai.api_key || j.openrouter_api_key || ''
    aiModel.value = ai.model || j.openrouter_model || 'google/gemini-2.0-flash-exp:free'
  }
}
async function saveAdminSettings(silent = false) {
  await fetch('/api/settings', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ...settingsData.value,
      language: settingsData.value.language,
      network_unit: settingsData.value.network_unit,
      thresholds: settingsData.value.thresholds,
      notifications_enabled: settingsData.value.notifications_enabled !== false,
      notifications: {
        enabled: settingsData.value.notifications_enabled !== false,
        telegram_token: telegramToken.value,
        telegram_chat_id: telegramChatId.value,
        discord_webhook: discordWebhook.value,
      },
      ai_provider: settingsData.value.ai_provider || 'openrouter',
      ai_enabled: Boolean(settingsData.value.ai_enabled),
      ai: {
        enabled: Boolean(settingsData.value.ai_enabled),
        provider: settingsData.value.ai_provider || 'openrouter',
        api_key: aiApiKey.value,
        model: aiModel.value,
      },
    })
  })
  if (!silent) {
    alert('Configurações salvas com sucesso!')
  }
}

const appUpdateInfo = ref({ current_version: APP_VERSION, latest_version: APP_VERSION, update_available: { stable: false } })
const appUpdating = ref(false)
const appUpdateMsg = ref('')

async function fetchAppUpdateStatus(force = false) {
  try {
    const res = await fetch(`/api/proxmenux/update-status?force=${force ? 'true' : 'false'}`)
    if (res.ok) {
      appUpdateInfo.value = await res.json()
    }
  } catch {}
}

const selfUpdateModalOpen = ref(false)
const selfUpdateTarget = ref('')
const selfUpdateLog = ref('')
const selfUpdateStatus = ref('running')
const selfUpdateStatusMsg = ref('Atualizando em tempo real...')
let selfUpdatePollTimer = null

function reloadAfterSelfUpdate() {
  window.location.reload()
}

function closeSelfUpdateModal() {
  if (selfUpdateStatus.value === 'running' || selfUpdateStatus.value === 'restarting') return
  selfUpdateModalOpen.value = false
  if (selfUpdatePollTimer) {
    clearInterval(selfUpdatePollTimer)
    selfUpdatePollTimer = null
  }
}

async function triggerAppSelfUpdate() {
  if (appUpdating.value) return
  appUpdating.value = true
  const expectedVer = appUpdateInfo.value?.latest_version || ''
  selfUpdateTarget.value = expectedVer
  selfUpdateLog.value = `:: Preparando atualização para v${expectedVer || 'nova versão'}...\n`
  selfUpdateStatus.value = 'running'
  selfUpdateStatusMsg.value = 'Baixando e aplicando atualização...'
  healthModalOpen.value = false
  selfUpdateModalOpen.value = true
  appUpdateMsg.value = 'Baixando e aplicando nova versão do repositório...'

  try {
    const res = await fetch('/api/proxmenux/self-update', { method: 'POST' })
    const data = await res.json().catch(() => ({}))
    if (!res.ok) {
      selfUpdateStatus.value = 'error'
      selfUpdateStatusMsg.value = data.detail || 'Falha ao iniciar atualização.'
      selfUpdateLog.value += `\n✗ ${selfUpdateStatusMsg.value}\n`
      appUpdateMsg.value = selfUpdateStatusMsg.value
      appUpdating.value = false
      return
    }

    if (data.target_version) selfUpdateTarget.value = data.target_version
    const target = selfUpdateTarget.value
    let sawRestart = false
    let ticks = 0

    if (selfUpdatePollTimer) clearInterval(selfUpdatePollTimer)
    selfUpdatePollTimer = setInterval(async () => {
      ticks += 1
      if (ticks > 150) {
        clearInterval(selfUpdatePollTimer)
        selfUpdatePollTimer = null
        selfUpdateStatus.value = 'error'
        selfUpdateStatusMsg.value = 'Tempo limite excedido aguardando conclusão.'
        appUpdating.value = false
        return
      }
      try {
        const logRes = await fetch('/api/proxmenux/self-update/log')
        if (!logRes.ok) throw new Error('restarting')
        const d = await logRes.json()
        if (d.log) selfUpdateLog.value = d.log

        if (d.failed) {
          clearInterval(selfUpdatePollTimer)
          selfUpdatePollTimer = null
          selfUpdateStatus.value = 'error'
          selfUpdateStatusMsg.value = 'Falha durante a execução do instalador.'
          appUpdating.value = false
          return
        }

        const versionMatched = target && d.current_version === target
        if (d.done && (versionMatched || sawRestart || !d.running)) {
          clearInterval(selfUpdatePollTimer)
          selfUpdatePollTimer = null
          selfUpdateStatus.value = 'done'
          selfUpdateStatusMsg.value = `Atualizado para v${d.current_version || target}! Recarregando...`
          appUpdating.value = false
          setTimeout(() => window.location.reload(), 1500)
          return
        }

        if (sawRestart && versionMatched) {
          clearInterval(selfUpdatePollTimer)
          selfUpdatePollTimer = null
          selfUpdateStatus.value = 'done'
          selfUpdateStatusMsg.value = `Atualizado para v${d.current_version}! Recarregando...`
          appUpdating.value = false
          setTimeout(() => window.location.reload(), 1500)
          return
        }

        selfUpdateStatus.value = 'running'
        selfUpdateStatusMsg.value = 'Executando instalador e aplicando arquivos...'
      } catch {
        sawRestart = true
        selfUpdateStatus.value = 'restarting'
        selfUpdateStatusMsg.value = 'Reiniciando serviço linuxmenux.service...'
      }
    }, 1200)
  } catch (e) {
    selfUpdateStatus.value = 'error'
    selfUpdateStatusMsg.value = 'Erro de conexão ao iniciar atualização.'
    selfUpdateLog.value += '\n✗ Erro de conexão ao iniciar atualização.\n'
    appUpdateMsg.value = selfUpdateStatusMsg.value
    appUpdating.value = false
  }
}

async function openHealthModal(defaultCat = 'updates', forceUpdates = false) {
  healthModalOpen.value = true
  expandedHealthCat.value = defaultCat
  healthLoading.value = true
  try {
    const [res] = await Promise.all([
      fetch(`/api/health/full?force_updates=${forceUpdates ? 'true' : 'false'}`),
      fetchAppUpdateStatus(forceUpdates),
    ])
    if (res.ok) {
      healthData.value = await res.json()
    }
  } catch (e) {
    console.error('Erro ao carregar saúde do sistema:', e)
  } finally {
    healthLoading.value = false
  }
}

async function openSystemUpdateModal() {
  updateModalOpen.value = true
  updateWsState.value = 'connecting'
  await nextTick()
  if (!updateTerminalContainer.value) return

  if (updateWs) { try { updateWs.close() } catch (e) {} }
  if (updateXterm) { try { updateXterm.dispose() } catch (e) {} }

  updateXterm = new XTerm({
    cursorBlink: true,
    fontSize: 13,
    fontFamily: 'monospace',
    scrollback: 5000,
    theme: { background: '#000000', foreground: '#f4f4f5' }
  })
  updateFitAddon = new FitAddon()
  updateXterm.loadAddon(updateFitAddon)
  updateXterm.open(updateTerminalContainer.value)
  updateFitAddon.fit()

  try {
    const tRes = await fetch('/api/terminal/ticket', { method: 'POST' })
    const tJson = await tRes.json()
    const wsProto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    updateWs = new WebSocket(`${wsProto}//${window.location.host}/ws/system-update?ticket=${tJson.ticket}`)
    updateWs.onopen = () => { updateWsState.value = 'online' }
    updateWs.onmessage = (ev) => { if (updateXterm) updateXterm.write(ev.data) }
    updateWs.onclose = () => { updateWsState.value = 'offline' }
    updateWs.onerror = () => { updateWsState.value = 'offline' }
  } catch (err) {
    updateWsState.value = 'offline'
    if (updateXterm) updateXterm.writeln(`\r\n\x1b[31mErro: ${err.message}\x1b[0m`)
  }
}

async function closeSystemUpdateModal() {
  if (updateWs) { try { updateWs.close() } catch (e) {} updateWs = null }
  updateModalOpen.value = false
  await openHealthModal('updates', true)
  await fetchTelemetry()
}

// AI Diagnosis State
const aiLoading = ref(false)
const aiReport = ref(null)

// Notification Inputs
const telegramToken = ref('')
const telegramChatId = ref('')
const discordWebhook = ref('')

// Chart Canvas References
const overviewRef = ref(null)
const networkRef = ref(null)
const terminalRef = ref(null)
const updateModalRef = ref(null)
const cpuChartCanvas = computed(() => overviewRef.value?.cpuChartCanvas || null)
const memChartCanvas = computed(() => overviewRef.value?.memChartCanvas || null)
const overviewNetChartCanvas = computed(() => overviewRef.value?.overviewNetChartCanvas || null)
const netChartCanvas = computed(() => networkRef.value?.netChartCanvas || null)
const terminalContainer = computed(() => terminalRef.value?.terminalContainer || null)
const updateTerminalContainer = computed(() => updateModalRef.value?.updateTerminalContainer || null)

let cpuChart = null
let memChart = null
let netChart = null
let overviewNetChart = null

// Interactive PTY Terminal State
// terminalContainer provided via terminalRef computed above
const terminalConnected = ref(false)
const terminalConnecting = ref(false)
let xtermInstance = null
let fitAddonInstance = null
let terminalWs = null

// Network Flow Topology Data (Dynamic Telemetry)
const flowData = ref({
  nics: [],
  bridges: [],
  consumers: [],
  host_rate: '0 B/s'
})

const flowConsumers = computed(() => {
  return (flowData.value.consumers || []).filter(c => c.kind !== 'host')
})

async function fetchFlowData() {
  if (authGate.value !== 'ready') return
  try {
    const res = await fetch('/api/network/flow')
    if (res.ok) {
      const data = await res.json()
      flowData.value = data
    }
  } catch (err) {
    console.error('Erro ao buscar fluxo de rede:', err)
  }
}

async function initTerminal() {
  if (!terminalContainer.value) return
  terminalConnecting.value = true

  if (terminalWs) {
    try { terminalWs.close() } catch (e) {}
    terminalWs = null
  }
  if (xtermInstance) {
    try { xtermInstance.dispose() } catch (e) {}
    xtermInstance = null
  }

  try {
    const ticketRes = await fetch('/api/terminal/ticket', { method: 'POST' })
    if (!ticketRes.ok) throw new Error('Falha ao obter ticket seguro para o terminal')
    const ticketData = await ticketRes.json()
    const ticket = ticketData.ticket

    xtermInstance = new XTerm({
      cursorBlink: true,
      fontSize: 15,
      fontFamily: '"MesloLGS NF", "FiraCode Nerd Font", "JetBrainsMono Nerd Font", "Hack Nerd Font", monospace',
      lineHeight: 1.2,
      scrollback: 5000,
      theme: {
        background: '#000000',
        foreground: '#f4f4f5',
        cursor: '#f4f4f5',
        black: '#27272a',
        red: '#ef4444',
        green: '#10b981',
        yellow: '#f59e0b',
        blue: '#3b82f6',
        magenta: '#a855f7',
        cyan: '#06b6d4',
        white: '#f4f4f5',
        brightBlack: '#71717a',
        brightRed: '#f87171',
        brightGreen: '#34d399',
        brightYellow: '#fbbf24',
        brightBlue: '#60a5fa',
        brightMagenta: '#c084fc',
        brightCyan: '#22d3ee',
        brightWhite: '#ffffff'
      }
    })

    fitAddonInstance = new FitAddon()
    xtermInstance.loadAddon(fitAddonInstance)
    xtermInstance.open(terminalContainer.value)
    fitAddonInstance.fit()

    const wsProto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${wsProto}//${window.location.host}/ws/terminal?ticket=${ticket}`
    terminalWs = new WebSocket(wsUrl)

    terminalWs.onopen = () => {
      terminalConnected.value = true
      terminalConnecting.value = false
      if (fitAddonInstance && xtermInstance) {
        fitAddonInstance.fit()
        terminalWs.send(JSON.stringify({
          type: 'resize',
          cols: xtermInstance.cols,
          rows: xtermInstance.rows
        }))
      }
    }

    terminalWs.onmessage = (event) => {
      if (xtermInstance) {
        xtermInstance.write(event.data)
      }
    }

    terminalWs.onerror = (err) => {
      console.error('Terminal WS error:', err)
      terminalConnected.value = false
      terminalConnecting.value = false
    }

    terminalWs.onclose = () => {
      terminalConnected.value = false
      terminalConnecting.value = false
      if (xtermInstance) {
        xtermInstance.writeln('\r\n\x1b[31m[Conexão com o terminal encerrada. Clique em Reconectar Terminal para reiniciar.]\x1b[0m')
      }
    }

    xtermInstance.onData((data) => {
      if (terminalWs && terminalWs.readyState === WebSocket.OPEN) {
        terminalWs.send(data)
      }
    })

  } catch (err) {
    console.error('Erro ao inicializar terminal:', err)
    terminalConnected.value = false
    terminalConnecting.value = false
    if (xtermInstance) {
      xtermInstance.writeln(`\r\n\x1b[31mErro: ${err.message}\x1b[0m`)
    }
  }
}

function reconnectTerminal() {
  initTerminal()
}

function sendTerminalCommand(cmd) {
  if (terminalWs && terminalWs.readyState === WebSocket.OPEN) {
    terminalWs.send(cmd + '\n')
    if (xtermInstance) xtermInstance.focus()
  } else {
    reconnectTerminal()
    setTimeout(() => {
      if (terminalWs && terminalWs.readyState === WebSocket.OPEN) {
        terminalWs.send(cmd + '\n')
      }
    }, 1200)
  }
}

async function loadDataForTab(tab) {
  if (tab === 'overview') {
    await nextTick()
    initCharts()
    updateMetricsCharts()
    updateOverviewNetChart()
  } else if (tab === 'terminal') {
    nextTick(() => {
      initTerminal()
    })
  } else if (tab === 'network-flow' || tab.startsWith('network')) {
    await nextTick()
    if (tab === 'network-overview') {
      initCharts()
      updateOverviewNetChart()
    }
    fetchFlowData()
  } else if (tab === 'apps') {
    fetchCustomLinks()
    fetchAppOverrides()
  } else if (tab === 'containers') {
    fetchContainerUpdates()
  } else if (tab === 'storage') {
    fetchStorageDisks()
  } else if (tab === 'hardware') {
    fetchHardwareFull()
  } else if (tab === 'backup') {
    fetchBackups()
  } else if (tab === 'admin-logs') {
    fetchLogs()
    fetchBackups()
  } else if (tab === 'admin-security') {
    fetchSecurity()
  } else if (tab === 'admin-audit') {
    fetchAuditReport()
  } else if (tab === 'admin-settings' || tab === 'admin') {
    fetchAdminSettings()
  }
}

watch(activeTab, async (newTab) => {
  await loadDataForTab(newTab)
})

// Real Telemetry Reactive Data (100% Real - Zero Mocks)
const systemData = ref({
  hostname: '',
  cpu_usage: 0,
  cpu_user: 0,
  cpu_system: 0,
  cpu_cores: 0,
  cpu_threads: 0,
  memory_usage: 0,
  memory_used: 0,
  memory_total: 0,
  memory_cached: 0,
  temperature: 0,
  uptime: 'Carregando...',
  kernel_version: '',
  is_virtual: false,
})

const containerStats = ref({
  total: 0,
  running: 0,
  stopped: 0,
})

const containers = ref([])

const containerSearch = ref('')
const containerUpdatesOnly = ref(false)
const containerUpdatesMap = ref({})
const checkingContainerUpdates = ref(false)
const updatingContainerId = ref('')
const containerLogsModalOpen = ref(false)
const containerLogsTitle = ref('')
const containerLogsText = ref('')

const containersWithUpdatesCount = computed(() => {
  return Object.values(containerUpdatesMap.value).filter(u => u.has_update).length
})

const filteredContainers = computed(() => {
  let list = containers.value
  if (containerUpdatesOnly.value) {
    list = list.filter(c => containerUpdatesMap.value[c.id]?.has_update)
  }
  if (containerSearch.value) {
    list = list.filter(c => c.name.toLowerCase().includes(containerSearch.value.toLowerCase()))
  }
  return list
})

function formatContainerPorts(ports) {
  if (!Array.isArray(ports) || !ports.length) return 'Host/Bridge'
  const formatted = ports.map(p => {
    if (typeof p === 'string') return p
    if (p && typeof p === 'object') {
      const priv = p.PrivatePort || ''
      const pub = p.PublicPort || ''
      const typ = p.Type || 'tcp'
      return pub ? `${pub}:${priv}/${typ}` : `${priv}/${typ}`
    }
    return String(p)
  }).filter(Boolean)
  return formatted.length ? [...new Set(formatted)].join(', ') : 'Host/Bridge'
}

async function fetchContainerUpdates(force = false) {
  checkingContainerUpdates.value = true
  try {
    const res = await fetch(`/api/lxc-updates/detection?force=${force ? 'true' : 'false'}`)
    if (res.ok) {
      const j = await res.json()
      const map = {}
      for (const item of (j.updates || [])) {
        map[item.id] = item
      }
      containerUpdatesMap.value = map
    }
  } catch (e) {
    console.error('Erro ao verificar atualizações de containers:', e)
  } finally {
    checkingContainerUpdates.value = false
  }
}

async function updateSingleContainer(c) {
  updatingContainerId.value = c.id
  try {
    const res = await fetch(`/api/docker/containers/${c.id}/update`, { method: 'POST' })
    const j = await res.json()
    alert(j.success ? `Container ${c.name} atualizado com sucesso!` : (j.message || 'Falha ao atualizar container'))
    await fetchContainerUpdates(true)
  } finally {
    updatingContainerId.value = ''
  }
}

async function restartContainer(c) {
  await fetch(`/api/docker/containers/${c.id}/restart`, { method: 'POST' })
  await fetchTelemetry()
}

async function openContainerLogs(c) {
  containerLogsTitle.value = c.name
  containerLogsText.value = 'Carregando logs...'
  containerLogsModalOpen.value = true
  const res = await fetch(`/api/docker/containers/${c.id}/logs`)
  if (res.ok) {
    const j = await res.json()
    containerLogsText.value = j.logs || 'Sem logs.'
  }
}

const networkData = ref({
  default_interface: '',
  default_media: 'Ethernet',
  default_speed: '1 Gbps',
  default_ip: '',
  physical_active_count: 0,
  physical_total_count: 0,
  bridge_active_count: 0,
  bridge_total_count: 0,
  total_interfaces: 0,
  total_rx_formatted: '0 B',
  total_tx_formatted: '0 B',
  domain: '',
  dns_servers: [],
  interfaces: []
})

// Custom links from /api/apps/custom-links
const customLinks = ref([])
const appSearch = ref('')
const selectedCategory = ref('__all__')

const newLinkName = ref('')
const newLinkUrl = ref('')
const newLinkCategory = ref('Geral')
const newLinkLogo = ref('')

// Compute real Web Apps from discovered Docker/Dokploy containers
const containerApps = computed(() => {
  const apps = []
  for (const c of containers.value) {
    const ports = c.ports || []
    let webPort = null
    if (Array.isArray(ports)) {
      for (const p of ports) {
        const pStr = typeof p === 'string' ? p : `${p.PublicPort || p.PrivatePort || ''}`
        const match = pStr.match(/(\d+)/)
        if (match) {
          const portNum = parseInt(match[1])
          if ([80, 443, 3000, 3001, 8080, 8081, 8082, 8000, 8443, 9000, 9443, 5000, 5173].includes(portNum) || (!webPort && portNum > 80)) {
            webPort = portNum
          }
        }
      }
    }
    const domain = c.traefik_domains && c.traefik_domains[0] ? c.traefik_domains[0] : null
    if (webPort || domain) {
      const url = domain ? `https://${domain}` : `http://${window.location.hostname}:${webPort}`
      apps.push({
        id: `ct-${c.id}`,
        name: c.name,
        description: c.is_dokploy ? 'Serviço Dokploy' : (c.image || 'Container Docker'),
        category: c.stack || 'Containers',
        url: url,
        port: webPort ? `Porta ${webPort}` : (domain ? '443 (SSL Traefik)' : 'N/A'),
        running: c.status === 'running',
        isCustom: false,
        logo_url: null,
      })
    }
  }
  return apps
})

const allApps = computed(() => {
  const custom = customLinks.value.map(l => ({
    id: l.id,
    name: l.name,
    description: l.url,
    category: l.category || 'Geral',
    url: l.url,
    port: 'Link Web',
    running: true,
    isCustom: true,
    logo_url: l.logo_url || null,
  }))
  return [...custom, ...containerApps.value]
})

const categoriesList = computed(() => {
  const set = new Set(['Geral'])
  for (const a of allApps.value) {
    if (a.category) set.add(a.category)
  }
  return Array.from(set)
})

const filteredApps = computed(() => {
  let list = allApps.value
  if (selectedCategory.value !== '__all__') {
    list = list.filter(a => a.category === selectedCategory.value)
  }
  if (appSearch.value.trim()) {
    const q = appSearch.value.toLowerCase()
    list = list.filter(a => a.name.toLowerCase().includes(q) || a.description.toLowerCase().includes(q))
  }
  return list
})

const appOverrides = ref({})
async function fetchAppOverrides() {
  try {
    const res = await fetch('/api/apps/overrides')
    if (res.ok) appOverrides.value = await res.json()
  } catch (e) {
    console.error('Erro ao buscar overrides de apps:', e)
  }
}
async function saveAppOverride(payload) {
  const res = await fetch('/api/apps/overrides', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (res.ok) appOverrides.value = await res.json()
}

async function fetchCustomLinks() {
  try {
    const res = await fetch('/api/apps/custom-links')
    if (res.ok) {
      customLinks.value = await res.json()
    }
  } catch (e) {
    console.error('Erro ao buscar links customizados:', e)
  }
}

async function saveCustomLink() {
  if (!newLinkName.value.trim() || !newLinkUrl.value.trim()) {
    alert('Nome e URL são obrigatórios.')
    return
  }
  try {
    const res = await fetch('/api/apps/custom-links', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: newLinkName.value.trim(),
        url: newLinkUrl.value.trim(),
        category: newLinkCategory.value.trim() || 'Geral',
        logo_url: newLinkLogo.value.trim()
      })
    })
    if (res.ok) {
      customLinkModal.value = false
      newLinkName.value = ''
      newLinkUrl.value = ''
      newLinkLogo.value = ''
      await fetchCustomLinks()
    } else {
      const err = await res.json()
      alert(err.detail || 'Erro ao criar link')
    }
  } catch (err) {
    alert('Erro de conexão ao salvar link')
  }
}

async function removeCustomLink(id) {
  if (!confirm('Deseja realmente excluir este link?')) return
  try {
    const res = await fetch(`/api/apps/custom-links/${id}`, { method: 'DELETE' })
    if (res.ok) {
      await fetchCustomLinks()
    }
  } catch (e) {
    console.error('Erro ao excluir link:', e)
  }
}

// Fetch Telemetry from Backend
async function fetchTelemetry() {
  if (authGate.value !== 'ready') return
  try {
    const [sysRes, netRes, vmRes] = await Promise.all([
      fetch('/api/system').then(r => r.ok ? r.json() : null),
      fetch('/api/network').then(r => r.ok ? r.json() : null),
      fetch('/api/docker/containers?all=true').then(r => r.ok ? r.json() : null)
    ])

    if (sysRes) {
      systemData.value = {
        ...systemData.value,
        ...sysRes,
        memory_usage: sysRes.memory_percent || sysRes.memory_usage || 0,
        memory_used: sysRes.memory_used_gb || sysRes.memory_used || 0,
        memory_total: sysRes.memory_total_gb || sysRes.memory_total || 0,
        mounts: sysRes.mounts || sysRes.storage?.mounts || [],
        storage: sysRes.storage || {},
      }
    }

    if (netRes) {
      networkData.value = {
        ...networkData.value,
        ...netRes
      }
    }

    if (vmRes && Array.isArray(vmRes)) {
      containers.value = vmRes
      containerStats.value = {
        total: vmRes.length,
        running: vmRes.filter(v => v.status === 'running').length,
        stopped: vmRes.filter(v => v.status !== 'running').length
      }
    }
  } catch (err) {
    console.error('Erro ao buscar telemetria:', err)
  }
}

async function refreshAllData() {
  loading.value = true
  await fetchTelemetry()
  if (activeTab.value === 'storage') await fetchStorageDisks()
  else if (activeTab.value === 'hardware') await fetchHardwareFull()
  else if (activeTab.value === 'backup') await fetchBackups()
  else if (activeTab.value === 'admin-logs') await fetchLogs()
  else if (activeTab.value === 'admin-security') await fetchSecurity()
  else if (activeTab.value === 'admin-audit') await fetchAuditReport()
  setTimeout(() => { loading.value = false }, 400)
}

// AI Diagnosis Action
async function runAiDiagnosis() {
  aiLoading.value = true
  try {
    const res = await fetch('/api/ai/network-diagnosis', { method: 'POST' })
    if (res.ok) {
      aiReport.value = await res.json()
    }
  } catch (e) {
    console.error(e)
  } finally {
    aiLoading.value = false
  }
}

const ifaceModalOpen = ref(false)
const ifaceDetail = ref({})
async function openIfaceModal(iface) {
  ifaceDetail.value = { name: iface.name, status: iface.status, speed: iface.speed_str || iface.speed, mac: iface.mac, mtu: 1500, duplex: 'N/D', rx_bytes_formatted: '0 B', tx_bytes_formatted: '0 B', rx_packets: 0, tx_packets: 0, rx_errors: 0, tx_errors: 0, rx_dropped: 0, tx_dropped: 0 }
  ifaceModalOpen.value = true
  const res = await fetch(`/api/network/interface/${encodeURIComponent(iface.name)}`)
  if (res.ok) ifaceDetail.value = await res.json()
}

async function testTelegram() {
  const res = await fetch('/api/notifications/test', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ provider: 'telegram', telegram_token: telegramToken.value, telegram_chat_id: telegramChatId.value })
  })
  const j = await res.json()
  alert(j.message || 'Concluído')
}

async function testDiscord() {
  const res = await fetch('/api/notifications/test', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ provider: 'discord', discord_webhook: discordWebhook.value })
  })
  const j = await res.json()
  alert(j.message || 'Concluído')
}

let netChartUnit = 'MB'

// Chart Renderers
function initCharts() {
  const labels = ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00']

  // CPU Chart (Idêntico à Imagem 3)
  if (cpuChartCanvas.value) {
    if (cpuChart) cpuChart.destroy()
    cpuChart = new Chart(cpuChartCanvas.value, {
      type: 'line',
      data: {
        labels: [],
        datasets: [
          {
            label: 'CPU %',
            data: [],
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.18)',
            fill: true,
            tension: 0.35,
            borderWidth: 2,
            pointRadius: 0,
            pointHoverRadius: 4,
            yAxisID: 'y',
          },
          {
            label: 'Média de carga',
            data: [],
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.12)',
            fill: true,
            tension: 0.35,
            borderWidth: 1.8,
            pointRadius: 0,
            pointHoverRadius: 4,
            yAxisID: 'y1',
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { display: false },
          tooltip: {
            enabled: true,
            backgroundColor: '#18181b',
            borderColor: '#3f3f46',
            borderWidth: 1,
            padding: 10,
            cornerRadius: 8,
          }
        },
        scales: {
          x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#a1a1aa', font: { size: 11 }, maxTicksLimit: 8 } },
          y: {
            position: 'left',
            min: 0,
            suggestedMax: 100,
            title: { display: true, text: 'CPU %', color: '#a1a1aa', font: { size: 11 } },
            grid: { color: 'rgba(255,255,255,0.06)' },
            ticks: { color: '#a1a1aa', font: { size: 11 } }
          },
          y1: {
            position: 'right',
            min: 0,
            title: { display: true, text: 'Carregar', color: '#a1a1aa', font: { size: 11 } },
            grid: { drawOnChartArea: false },
            ticks: { color: '#a1a1aa', font: { size: 11 } }
          }
        }
      }
    })
  }

  // Memory Chart (Idêntico à Imagem 3)
  if (memChartCanvas.value) {
    if (memChart) memChart.destroy()
    memChart = new Chart(memChartCanvas.value, {
      type: 'line',
      data: {
        labels: [],
        datasets: [
          {
            label: 'Total',
            data: [],
            borderColor: '#3b82f6',
            borderWidth: 1.8,
            pointRadius: 0,
            pointHoverRadius: 4,
          },
          {
            label: 'Usado',
            data: [],
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.22)',
            fill: true,
            tension: 0.35,
            borderWidth: 2,
            pointRadius: 0,
            pointHoverRadius: 4,
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { display: false },
          tooltip: {
            enabled: true,
            backgroundColor: '#18181b',
            borderColor: '#3f3f46',
            borderWidth: 1,
            padding: 10,
            cornerRadius: 8,
            callbacks: {
              label: (ctx) => `${ctx.dataset.label}: ${Number(ctx.parsed.y || 0).toFixed(1)} GB`
            }
          }
        },
        scales: {
          x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#a1a1aa', font: { size: 11 }, maxTicksLimit: 8 } },
          y: {
            min: 0,
            title: { display: true, text: 'GB', color: '#a1a1aa', font: { size: 11 } },
            grid: { color: 'rgba(255,255,255,0.06)' },
            ticks: { color: '#a1a1aa', font: { size: 11 } }
          }
        }
      }
    })
  }

  // Network Traffic Chart (1:1 com hover tooltip por minuto)
  if (netChartCanvas.value) {
    if (netChart) netChart.destroy()
    netChart = new Chart(netChartCanvas.value, {
      type: 'line',
      data: {
        labels: [],
        datasets: [
          {
            label: 'Recebido',
            data: [],
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.15)',
            fill: true,
            tension: 0.35,
            borderWidth: 2,
            pointRadius: 0,
            pointHoverRadius: 4,
          },
          {
            label: 'Enviado',
            data: [],
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.15)',
            fill: true,
            tension: 0.35,
            borderWidth: 2,
            pointRadius: 0,
            pointHoverRadius: 4,
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { display: false },
          tooltip: {
            enabled: true,
            backgroundColor: '#18181b',
            borderColor: '#3f3f46',
            borderWidth: 1,
            padding: 10,
            cornerRadius: 8,
            callbacks: {
              label: (ctx) => `${ctx.dataset.label}: ${Number(ctx.parsed.y || 0).toFixed(3)} ${netChartUnit}`
            }
          }
        },
        scales: {
          x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#a1a1aa', font: { size: 11 }, maxTicksLimit: 8 } },
          y: {
            min: 0,
            title: { display: true, text: netChartUnit, color: '#a1a1aa', font: { size: 11 } },
            grid: { color: 'rgba(255,255,255,0.06)' },
            ticks: { color: '#a1a1aa', font: { size: 11 } }
          }
        }
      }
    })
  }

  // Overview Network Chart
  if (overviewNetChartCanvas.value) {
    if (overviewNetChart) overviewNetChart.destroy()
    overviewNetChart = new Chart(overviewNetChartCanvas.value, {
      type: 'line',
      data: {
        labels: [],
        datasets: [
          {
            label: 'Recebido',
            data: [],
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.15)',
            fill: true,
            tension: 0.35,
            borderWidth: 2,
            pointRadius: 0,
            pointHoverRadius: 4,
          },
          {
            label: 'Enviado',
            data: [],
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.15)',
            fill: true,
            tension: 0.35,
            borderWidth: 2,
            pointRadius: 0,
            pointHoverRadius: 4,
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { display: false },
          tooltip: {
            enabled: true,
            backgroundColor: '#18181b',
            borderColor: '#27272a',
            borderWidth: 1,
            callbacks: {
              label: (ctx) => `${ctx.dataset.label}: ${Number(ctx.parsed.y || 0).toFixed(2)} ${netChartUnit}`
            }
          }
        },
        scales: {
          x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#a1a1aa', font: { size: 11 }, maxTicksLimit: 7 } },
          y: {
            min: 0,
            title: { display: true, text: netChartUnit, color: '#a1a1aa', font: { size: 11 } },
            grid: { color: 'rgba(255,255,255,0.06)' },
            ticks: { color: '#a1a1aa', font: { size: 11 } }
          }
        }
      }
    })
  }

  updateMetricsCharts()
  updateOverviewNetChart()
}

function formatMetricLabel(ts, tf) {
  const d = new Date(ts)
  if (tf === 'hour' || tf === 'day') {
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }
  if (tf === 'year') {
    return d.toLocaleDateString('pt-BR', { month: 'short', year: 'numeric' })
  }
  return d.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' })
}

async function updateMetricsCharts() {
  metricsLoading.value = true
  try {
    const res = await fetch(`/api/node/metrics?timeframe=${timeframe.value}`)
    if (!res.ok) return
    const json = await res.json()
    if (!json.data || !json.data.length) return

    const labels = json.data.map(p => formatMetricLabel(p.time || p.timestamp, timeframe.value))
    const cpuData = json.data.map(p => p.cpu_percent !== undefined ? p.cpu_percent : Math.round((p.cpu || 0) * 100))
    const loadData = json.data.map(p => p.loadavg || 0)
    const memTotalGB = json.data.map(p => +(p.memtotal / (1024 ** 3)).toFixed(1))
    const memUsedGB = json.data.map(p => +(p.memused / (1024 ** 3)).toFixed(1))

    if (cpuChart) {
      const pr = labels.length <= 3 ? 3 : 0
      cpuChart.data.labels = labels
      cpuChart.data.datasets[0].data = cpuData
      cpuChart.data.datasets[0].pointRadius = pr
      cpuChart.data.datasets[1].data = loadData
      cpuChart.data.datasets[1].pointRadius = pr
      cpuChart.update()
    }
    if (memChart) {
      const pr = labels.length <= 3 ? 3 : 0
      memChart.data.labels = labels
      memChart.data.datasets[0].data = memTotalGB
      memChart.data.datasets[0].pointRadius = pr
      memChart.data.datasets[1].data = memUsedGB
      memChart.data.datasets[1].pointRadius = pr
      memChart.update()
    }
    if (json.period_stats?.cpu) {
      cpuStats.value = json.period_stats.cpu
    }
    if (json.period_stats?.memory_used) {
      memStats.value = json.period_stats.memory_used
    }
  } catch (err) {
    console.error('Erro ao atualizar gráficos de métricas:', err)
  } finally {
    metricsLoading.value = false
  }
}

async function updateOverviewNetChart() {
  netMetricsLoading.value = true
  try {
    const res = await fetch(`/api/node/metrics?timeframe=${netTimeframe.value}`)
    if (!res.ok) return
    const json = await res.json()
    if (json.period_stats?.network) {
      netPeriodStats.value = {
        rx_gb: json.period_stats.network.rx_gb ?? 0,
        tx_gb: json.period_stats.network.tx_gb ?? 0,
        rx_display: json.period_stats.network.rx_display,
        tx_display: json.period_stats.network.tx_display,
      }
    }
    const netPts = (json.network_data && json.network_data.length) ? json.network_data : (json.data || [])
    if (!netPts.length) return
    const labels = netPts.map(p => formatMetricLabel(p.time || p.timestamp, netTimeframe.value))
    const maxBytes = Math.max(...netPts.map(p => Math.max(p.rx ?? p.netin ?? 0, p.tx ?? p.netout ?? 0)), 0)
    let divisor = 1024 ** 2
    if (maxBytes < 1024 * 1024) {
      netChartUnit = 'KB'
      divisor = 1024
    } else if (maxBytes < 1024 ** 3) {
      netChartUnit = 'MB'
      divisor = 1024 ** 2
    } else {
      netChartUnit = 'GB'
      divisor = 1024 ** 3
    }
    const rxVals = netPts.map(p => +(((p.rx ?? p.netin ?? 0)) / divisor).toFixed(3))
    const txVals = netPts.map(p => +(((p.tx ?? p.netout ?? 0)) / divisor).toFixed(3))

    if (overviewNetChart) {
      const pr = labels.length <= 3 ? 3 : 0
      overviewNetChart.data.labels = labels
      overviewNetChart.data.datasets[0].data = rxVals
      overviewNetChart.data.datasets[0].pointRadius = pr
      overviewNetChart.data.datasets[1].data = txVals
      overviewNetChart.data.datasets[1].pointRadius = pr
      overviewNetChart.options.scales.y.title.text = netChartUnit
      overviewNetChart.update()
    }
    if (netChart) {
      netChart.data.labels = labels
      netChart.data.datasets[0].data = rxVals
      netChart.data.datasets[1].data = txVals
      netChart.options.scales.y.title.text = netChartUnit
      netChart.update()
    }
  } catch (err) {
    console.error('Erro ao atualizar gráfico de rede:', err)
  } finally {
    netMetricsLoading.value = false
  }
}

watch(timeframe, () => {
  updateMetricsCharts()
})

watch(netTimeframe, () => {
  updateOverviewNetChart()
})

const handleResize = () => {
  if (fitAddonInstance) {
    try {
      fitAddonInstance.fit()
      if (terminalWs && terminalWs.readyState === WebSocket.OPEN && xtermInstance) {
        terminalWs.send(JSON.stringify({
          type: 'resize',
          cols: xtermInstance.cols,
          rows: xtermInstance.rows
        }))
      }
    } catch (e) {}
  }
}

onMounted(async () => {
  try {
    const urlTok = new URLSearchParams(window.location.search).get('token')
    if (urlTok && urlTok.trim()) {
      setAuthToken(urlTok.trim())
      window.history.replaceState({}, '', window.location.pathname)
    }
    const savedTheme = localStorage.getItem('linuxmenux-theme')
    if (savedTheme === 'light') isDarkTheme.value = false
  } catch {}

  try {
    const authRes = await fetch('/api/auth/status')
    if (authRes.ok) {
      const authStatus = await authRes.json()
      if (authStatus.needs_setup || (!authStatus.configured && !authStatus.declined)) {
        authGate.value = 'setup'
      } else if (authStatus.enabled && !getAuthToken()) {
        authGate.value = 'login'
      } else {
        authGate.value = 'ready'
        if (authStatus.username) currentUsername.value = authStatus.username
        checkFirstVisitModals()
      }
    }
  } catch {}

  window.addEventListener('linuxmenux:unauthorized', () => {
    setAuthToken('')
    authGate.value = 'login'
  })

  window.addEventListener('resize', handleResize)
  window.addEventListener('keydown', handleGlobalEscape)

  if (authGate.value === 'ready') {
    await startDashboardSession()
  }
})

let dashboardSessionStarted = false
async function startDashboardSession() {
  if (dashboardSessionStarted) {
    await fetchTelemetry()
    await fetchFlowData()
    return
  }
  dashboardSessionStarted = true
  await fetchTelemetry()
  await fetchFlowData()
  fetchAppUpdateStatus()
  await fetchCustomLinks()
  await fetchAppOverrides()
  fetchStorageDisks()
  fetchContainerUpdates()
  fetchAdminSettings()
  await nextTick()
  initCharts()
  await loadDataForTab(activeTab.value)
  setInterval(fetchTelemetry, 3000)
  setInterval(fetchFlowData, 2000)
  setInterval(() => {
    if (authGate.value !== 'ready') return
    updateMetricsCharts()
    updateOverviewNetChart()
  }, 15000)
}

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('keydown', handleGlobalEscape)
  if (terminalWs) terminalWs.close()
  if (xtermInstance) xtermInstance.dispose()
})
</script>

<style scoped>
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(3px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fadeIn {
  animation: fadeIn 0.25s ease-out forwards;
}
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
