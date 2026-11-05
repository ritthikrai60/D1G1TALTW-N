<!--
  InventoryPalette Component
  Displays real scanned unplaced network hardware from LUDUS Digital Twin (Inventory)
  Allows drag-and-drop directly into 19-inch racks.
-->
<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { getLayoutStore } from "$lib/stores/layout.svelte";
  import {
    createPaletteDragData,
    serializeDragData,
    setCurrentDragData,
    hideNativeDragGhost,
  } from "$lib/utils/dragdrop";
  import {
    showDragTooltip,
    updateDragTooltipPosition,
    hideDragTooltip,
  } from "$lib/stores/dragTooltip.svelte";
  import IconGrip from "./icons/IconGrip.svelte";
  import { ICON_SIZE } from "$lib/constants/sizing";
  import type { DeviceType } from "$lib/types";

  interface InventoryDevice {
    id: string;
    name: string;
    ip: string;
    mac: string;
    vendor: string;
    category: string;
    modelType: string;
    status: string;
    uHeight: number;
    isFullDepth: boolean;
  }

  const layoutStore = getLayoutStore();

  let devices = $state<InventoryDevice[]>([]);
  let loading = $state(true);
  let error = $state<string | null>(null);
  let searchQuery = $state("");
  let selectedCategory = $state("All");

  let syncChannel: BroadcastChannel | null = null;

  async function fetchInventory() {
    try {
      loading = true;
      error = null;
      const res = await fetch("/api/inventory");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      devices = Array.isArray(data.devices) ? data.devices : [];
    } catch (err: any) {
      error = err.message || "Failed to load inventory";
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    fetchInventory();

    if (typeof BroadcastChannel !== "undefined") {
      syncChannel = new BroadcastChannel("ludus_digital_twin_sync");
      syncChannel.onmessage = (event) => {
        if (event.data?.type === "state_changed" || event.data?.type === "rack_updated") {
          fetchInventory();
        }
      };
    }
  });

  onDestroy(() => {
    if (syncChannel) {
      syncChannel.close();
      syncChannel = null;
    }
  });

  const categories = $derived([
    "All",
    ...Array.from(new Set(devices.map((d) => d.category || "Other"))),
  ]);

  const filteredDevices = $derived(
    devices.filter((dev) => {
      const matchCat =
        selectedCategory === "All" || dev.category === selectedCategory;
      const q = searchQuery.toLowerCase().trim();
      if (!q) return matchCat;
      const matchSearch =
        dev.name.toLowerCase().includes(q) ||
        dev.ip.toLowerCase().includes(q) ||
        dev.mac.toLowerCase().includes(q) ||
        dev.vendor.toLowerCase().includes(q);
      return matchCat && matchSearch;
    })
  );

  function getCategoryColor(cat: string): string {
    switch ((cat || "").toLowerCase()) {
      case "server":
        return "#10b981";
      case "switch":
        return "#3b82f6";
      case "router":
      case "gateway":
        return "#f59e0b";
      case "access point":
      case "ap":
        return "#06b6d4";
      case "camera":
      case "cctv":
        return "#ec4899";
      case "ups":
      case "pdu":
        return "#8b5cf6";
      default:
        return "#64748b";
    }
  }

  function createDeviceTypeForInventory(dev: InventoryDevice): DeviceType {
    return {
      slug: dev.id,
      model: dev.name,
      manufacturer: dev.vendor || "Generic",
      u_height: dev.uHeight || (dev.category === "Server" ? 2 : 1),
      category: dev.category as any,
      is_full_depth: dev.isFullDepth ?? true,
      colour: getCategoryColor(dev.category),
    };
  }

  function handleDragStart(event: DragEvent, dev: InventoryDevice) {
    if (!event.dataTransfer) return;
    const type = createDeviceTypeForInventory(dev);

    // Ensure the device type is registered in the layout's library so rack renderer can resolve it
    if (!layoutStore.device_types.some((dt) => dt.slug === type.slug)) {
      layoutStore.addDeviceTypeRaw(type);
    }

    const dragData = createPaletteDragData(type);
    event.dataTransfer.setData("application/json", serializeDragData(dragData));
    event.dataTransfer.setData("text/plain", serializeDragData(dragData));
    event.dataTransfer.effectAllowed = "copy";
    setCurrentDragData(dragData);
    hideNativeDragGhost(event);
    showDragTooltip(event, { device: type, isCompatible: true });
  }

  function handleDrag(event: DragEvent) {
    updateDragTooltipPosition(event);
  }

  function handleDragEnd() {
    setCurrentDragData(null);
    hideDragTooltip();
  }
</script>

<div class="inventory-palette" data-testid="inventory-palette">
  <!-- Search and Header -->
  <div class="inventory-header">
    <div class="inventory-title-row">
      <span class="inventory-title">📦 Real Hardware</span>
      <span class="inventory-count-badge">{devices.length}</span>
      <button
        type="button"
        class="inventory-refresh-btn"
        title="Refresh Inventory"
        onclick={fetchInventory}
        aria-label="Refresh Inventory"
      >
        🔄
      </button>
    </div>
    <input
      type="text"
      placeholder="Search IP, name, MAC, vendor..."
      class="inventory-search"
      bind:value={searchQuery}
    />
  </div>

  <!-- Category filter chips -->
  <div class="inventory-categories" role="tablist" aria-label="Device categories">
    {#each categories as cat}
      <button
        type="button"
        class="category-chip"
        class:category-chip--active={selectedCategory === cat}
        onclick={() => (selectedCategory = cat)}
      >
        {cat}
      </button>
    {/each}
  </div>

  <!-- Device List -->
  <div class="inventory-list">
    {#if loading}
      <div class="inventory-loading">Loading inventory...</div>
    {:else if error}
      <div class="inventory-error">
        <span>⚠️ {error}</span>
        <button type="button" onclick={fetchInventory} class="retry-btn">Retry</button>
      </div>
    {:else if filteredDevices.length === 0}
      <div class="inventory-empty">
        {searchQuery ? "No devices match search" : "No unplaced devices in inventory"}
      </div>
    {:else}
      {#each filteredDevices as dev (dev.id)}
        <div
          class="inventory-item"
          draggable="true"
          ondragstart={(e) => handleDragStart(e, dev)}
          ondrag={handleDrag}
          ondragend={handleDragEnd}
          role="listitem"
          title="Drag into rack slot"
        >
          <div class="grip-handle" aria-hidden="true">
            <IconGrip size={ICON_SIZE.sm} />
          </div>

          <div class="item-status" class:status--online={dev.status === "Online"}></div>

          <div class="item-content">
            <div class="item-row-top">
              <span class="item-name">{dev.name}</span>
              <span class="item-u-badge">{dev.uHeight || 1}U</span>
            </div>

            <div class="item-row-bottom">
              <span class="item-ip">{dev.ip || "No IP"}</span>
              <span
                class="item-category"
                style="border-color: {getCategoryColor(dev.category)}40; color: {getCategoryColor(dev.category)}"
              >
                {dev.category}
              </span>
            </div>

            {#if dev.vendor}
              <div class="item-vendor">{dev.vendor}</div>
            {/if}
          </div>
        </div>
      {/each}
    {/if}
  </div>
</div>

<style>
  .inventory-palette {
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
    background: var(--colour-sidebar-bg, #1a1a24);
    color: var(--colour-text, #f8fafc);
  }

  .inventory-header {
    padding: var(--space-2, 8px);
    border-bottom: 1px solid var(--colour-border, #334155);
    display: flex;
    flex-direction: column;
    gap: 6px;
    background: rgba(0, 0, 0, 0.15);
  }

  .inventory-title-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 13px;
    font-weight: 600;
  }

  .inventory-title {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .inventory-count-badge {
    background: var(--colour-primary-bg, #3b82f6);
    color: #fff;
    font-size: 11px;
    padding: 1px 6px;
    border-radius: 9999px;
    font-weight: 700;
  }

  .inventory-refresh-btn {
    background: transparent;
    border: none;
    cursor: pointer;
    font-size: 13px;
    opacity: 0.7;
    transition: opacity 0.15s;
    padding: 2px 4px;
  }
  .inventory-refresh-btn:hover {
    opacity: 1;
  }

  .inventory-search {
    width: 100%;
    padding: 6px 10px;
    font-size: 12px;
    background: var(--colour-input-bg, #0f172a);
    border: 1px solid var(--colour-border, #334155);
    border-radius: 6px;
    color: inherit;
    outline: none;
  }
  .inventory-search:focus {
    border-color: var(--colour-primary, #38bdf8);
  }

  .inventory-categories {
    display: flex;
    gap: 4px;
    padding: 6px 8px;
    overflow-x: auto;
    border-bottom: 1px solid var(--colour-border, #334155);
    flex-shrink: 0;
  }

  .category-chip {
    background: var(--colour-card-bg, #1e293b);
    border: 1px solid var(--colour-border, #334155);
    color: var(--colour-text-muted, #94a3b8);
    font-size: 10px;
    padding: 3px 8px;
    border-radius: 9999px;
    cursor: pointer;
    white-space: nowrap;
    transition: all 0.15s;
  }
  .category-chip:hover {
    background: #334155;
    color: #fff;
  }
  .category-chip--active {
    background: var(--colour-primary, #38bdf8);
    color: #0f172a;
    font-weight: 600;
    border-color: var(--colour-primary, #38bdf8);
  }

  .inventory-list {
    flex: 1;
    overflow-y: auto;
    padding: 8px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .inventory-loading,
  .inventory-empty,
  .inventory-error {
    padding: 24px 12px;
    text-align: center;
    font-size: 12px;
    color: var(--colour-text-muted, #94a3b8);
  }
  .inventory-error {
    color: #f87171;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }
  .retry-btn {
    background: #334155;
    border: none;
    color: #fff;
    padding: 4px 10px;
    border-radius: 4px;
    cursor: pointer;
  }

  .inventory-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 10px;
    background: var(--colour-card-bg, #1e293b);
    border: 1px solid var(--colour-border, #334155);
    border-radius: 8px;
    cursor: grab;
    transition: transform 0.1s, border-color 0.15s, background-color 0.15s;
    user-select: none;
  }
  .inventory-item:hover {
    background: #24324a;
    border-color: var(--colour-primary, #38bdf8);
    transform: translateY(-1px);
  }
  .inventory-item:active {
    cursor: grabbing;
  }

  .grip-handle {
    color: var(--colour-text-muted, #64748b);
    flex-shrink: 0;
  }

  .item-status {
    width: 7px;
    height: 7px;
    border-radius: 9999px;
    background: #64748b;
    flex-shrink: 0;
  }
  .status--online {
    background: #22c55e;
    box-shadow: 0 0 6px #22c55e80;
  }

  .item-content {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .item-row-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 4px;
  }

  .item-name {
    font-size: 12px;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .item-u-badge {
    font-size: 10px;
    font-weight: 700;
    background: rgba(255, 255, 255, 0.1);
    padding: 1px 4px;
    border-radius: 4px;
    color: #38bdf8;
    flex-shrink: 0;
  }

  .item-row-bottom {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 4px;
    font-size: 11px;
  }

  .item-ip {
    color: var(--colour-text-muted, #94a3b8);
    font-family: monospace;
    font-size: 10.5px;
  }

  .item-category {
    font-size: 9.5px;
    padding: 1px 5px;
    border-radius: 4px;
    border: 1px solid;
    text-transform: uppercase;
    font-weight: 600;
  }

  .item-vendor {
    font-size: 10px;
    color: #64748b;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
</style>
