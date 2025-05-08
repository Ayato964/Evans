import javax.sound.midi.*;
import javax.swing.*;
import javax.swing.filechooser.FileNameExtensionFilter;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.File;
import java.io.IOException;

public class MidiPlayerApp extends JFrame {

    private JButton playButton;
    private JButton selectFileButton;
    private JLabel statusLabel;
    private Sequencer sequencer;
    private String currentMidiFilePath = null;
    private String currentMidiFileName = "N/A";

    public MidiPlayerApp() {
        setTitle("MIDI Player");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(400, 200);
        setLocationRelativeTo(null);
        setLayout(new BorderLayout(10, 10));

        try {
            sequencer = MidiSystem.getSequencer();
            if (sequencer == null) {
                JOptionPane.showMessageDialog(this,
                        "MIDIシーケンサーが見つかりません。MIDI再生機能が利用できません。",
                        "初期化エラー", JOptionPane.ERROR_MESSAGE);
            } else {
                sequencer.open();
                sequencer.addMetaEventListener(meta -> {
                    if (meta.getType() == 47) { // End of Track
                        SwingUtilities.invokeLater(() -> {
                            statusLabel.setText("再生終了: " + currentMidiFileName);
                            playButton.setText("再生");
                            playButton.setEnabled(true);
                        });
                    }
                });
            }
        } catch (MidiUnavailableException e) {
            e.printStackTrace();
            JOptionPane.showMessageDialog(this,
                    "MIDIデバイスが利用できません: " + e.getMessage(),
                    "初期化エラー", JOptionPane.ERROR_MESSAGE);
            sequencer = null; // sequencer を null に設定して後続処理で判定できるようにする
        }

        JPanel topPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 10, 10));
        selectFileButton = new JButton("MIDIファイルを選択");
        playButton = new JButton("再生");
        playButton.setEnabled(false);

        topPanel.add(selectFileButton);
        topPanel.add(playButton);

        statusLabel = new JLabel("MIDIファイルを選択してください。", SwingConstants.CENTER);
        statusLabel.setBorder(BorderFactory.createEmptyBorder(10,10,10,10));

        add(topPanel, BorderLayout.NORTH);
        add(statusLabel, BorderLayout.CENTER);

        selectFileButton.addActionListener(e -> chooseMidiFile());

        playButton.addActionListener(e -> {
            if (playButton.getText().equals("再生")) {
                playMidi();
            } else {
                stopMidi();
            }
        });

        addWindowListener(new java.awt.event.WindowAdapter() {
            @Override
            public void windowClosing(java.awt.event.WindowEvent windowEvent) {
                if (sequencer != null && sequencer.isOpen()) {
                    if (sequencer.isRunning()) {
                        sequencer.stop();
                    }
                    sequencer.close();
                    System.out.println("MIDIシーケンサーをクローズしました。");
                }
            }
        });

        if (sequencer == null) { // sequencerが初期化できなかった場合
            playButton.setEnabled(false);
            // selectFileButton も無効化するかどうかは設計次第
            // selectFileButton.setEnabled(false);
            statusLabel.setText("MIDI機能が利用できません。");
        }
    }

    private void chooseMidiFile() {
        if (sequencer == null) { // シーケンサーが利用不可ならファイル選択もさせない方が良いかも
            JOptionPane.showMessageDialog(this,
                    "MIDI機能が利用できません。",
                    "エラー", JOptionPane.ERROR_MESSAGE);
            return;
        }
        JFileChooser fileChooser = new JFileChooser();
        fileChooser.setDialogTitle("MIDIファイルを選択");
        fileChooser.setFileFilter(new FileNameExtensionFilter("MIDI Files (*.mid, *.midi)", "mid", "midi"));
        int result = fileChooser.showOpenDialog(this);

        if (result == JFileChooser.APPROVE_OPTION) {
            File selectedFile = fileChooser.getSelectedFile();
            currentMidiFilePath = selectedFile.getAbsolutePath();
            currentMidiFileName = selectedFile.getName();
            statusLabel.setText("選択中: " + currentMidiFileName);
            playButton.setEnabled(true);
            if (sequencer.isRunning()) {
                stopMidi(); // 新しいファイルを選択したら、再生中のものは止める
                playButton.setText("再生"); // ボタンのテキストも戻す
            }
        }
    }

    private void playMidi() {
        if (sequencer == null || !sequencer.isOpen()) {
            JOptionPane.showMessageDialog(this,
                    "MIDIシーケンサーが利用できません。",
                    "再生エラー", JOptionPane.ERROR_MESSAGE);
            return;
        }

        if (currentMidiFilePath == null) {
            JOptionPane.showMessageDialog(this,
                    "再生するMIDIファイルが選択されていません。",
                    "ファイル未選択", JOptionPane.WARNING_MESSAGE);
            return;
        }

        try {
            File midiFile = new File(currentMidiFilePath);
            if (!midiFile.exists()) {
                JOptionPane.showMessageDialog(this,
                        "MIDIファイルが見つかりません: " + currentMidiFilePath,
                        "ファイルエラー", JOptionPane.ERROR_MESSAGE);
                currentMidiFilePath = null;
                currentMidiFileName = "N/A";
                playButton.setEnabled(false);
                statusLabel.setText("ファイルエラー。再度選択してください。");
                return;
            }

            Sequence sequence = MidiSystem.getSequence(midiFile);

            if (sequencer.isRunning()) {
                sequencer.stop();
            }
            sequencer.setSequence(sequence);
            sequencer.setTickPosition(0);
            sequencer.start();

            statusLabel.setText("再生中: " + currentMidiFileName);
            playButton.setText("停止");

        } catch (InvalidMidiDataException e) {
            e.printStackTrace();
            JOptionPane.showMessageDialog(this,
                    "無効なMIDIデータです: " + e.getMessage(),
                    "再生エラー", JOptionPane.ERROR_MESSAGE);
            statusLabel.setText("エラー: 無効なMIDIデータ");
        } catch (IOException e) {
            e.printStackTrace();
            JOptionPane.showMessageDialog(this,
                    "ファイルの読み込みに失敗しました: " + e.getMessage(),
                    "I/Oエラー", JOptionPane.ERROR_MESSAGE);
            statusLabel.setText("エラー: ファイル読込失敗");
        } catch (IllegalStateException e) { // sequencer.setSequence や sequencer.start がスローする可能性
            e.printStackTrace();
            JOptionPane.showMessageDialog(this,
                    "シーケンサーの状態が不正です: " + e.getMessage(),
                    "再生エラー", JOptionPane.ERROR_MESSAGE);
            statusLabel.setText("エラー: シーケンサー状態不正");
            // 必要であれば、ここで playButton を無効化するなどの処理を追加
            // playButton.setEnabled(false);
        }
    }

    private void stopMidi() {
        if (sequencer != null && sequencer.isOpen() && sequencer.isRunning()) {
            sequencer.stop();
            statusLabel.setText("停止しました: " + currentMidiFileName);
            playButton.setText("再生");
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            MidiPlayerApp player = new MidiPlayerApp();
            player.setVisible(true);
        });
    }
}