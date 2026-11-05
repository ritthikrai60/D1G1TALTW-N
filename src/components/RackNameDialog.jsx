import React, { useEffect, useState } from "react"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

/**
 * Asks for the name of an EMPTY server rack before entering 3D placement mode.
 * Devices are mounted afterwards (Rackula: scanned devices or library parts).
 */
export function RackNameDialog({ open, defaultName, existingNames = [], onCancel, onConfirm }) {
  const [name, setName] = useState(defaultName || "")

  useEffect(() => {
    if (open) setName(defaultName || "")
  }, [open, defaultName])

  const trimmed = name.trim()
  const duplicate = existingNames.some((n) => String(n).trim().toLowerCase() === trimmed.toLowerCase())

  const submit = (e) => {
    e.preventDefault()
    if (!trimmed) return
    onConfirm(trimmed)
  }

  return (
    <Dialog open={open} onOpenChange={(next) => { if (!next) onCancel() }}>
      <DialogContent className="max-w-md">
        <form onSubmit={submit} className="space-y-4">
          <DialogHeader>
            <DialogTitle>ตั้งชื่อตู้ Rack ก่อนวาง</DialogTitle>
            <DialogDescription>
              วางตู้เปล่าบนโมเดล 3D ก่อน แล้วค่อยใส่อุปกรณ์ (Router, Switch, ...) ผ่าน Rackula ภายหลัง
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-1.5">
            <Label htmlFor="rack-name-input">ชื่อตู้ Rack</Label>
            <Input
              id="rack-name-input"
              autoFocus
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="เช่น Rack-01, MDF Rack"
              aria-invalid={duplicate}
            />
            {duplicate && (
              <p className="text-xs text-muted-foreground" role="status">
                ⚠ ชื่อนี้ซ้ำกับตู้ที่มีอยู่แล้ว (ยังบันทึกได้)
              </p>
            )}
          </div>

          <DialogFooter className="gap-2">
            <Button type="button" variant="ghost" onClick={onCancel}>
              ยกเลิก
            </Button>
            <Button type="submit" disabled={!trimmed}>
              เริ่มวางตู้บน 3D
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

